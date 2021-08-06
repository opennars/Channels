"""
 * The MIT License
 *
 * Copyright 2021 The OpenNARS authors.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 * """
 
import sys
import os
import json
import subprocess
try:
    from subprocess import DEVNULL
except ImportError: #Python2 backwards compatibility:
    input = raw_input
    DEVNULL = open(os.devnull, 'wb')

def invoke(s):
    return eval(subprocess.check_output(s, shell=True, stderr=DEVNULL))

while True:
    subjects = [] #TODO better linking between words and concepts for assigning relation arguments
    #1. get entities
    cmd = """curl --request POST --url http://localhost:8081/factextraction/analyze   --header 'accept: application/json'   --header 'content-type: application/json'   --data '{"docId": "doc1", "text": "%s", "extractConcepts": "true", "language" : "en" }'"""
    sentence = input("") #"Jack founded Alibaba with investments from SoftBank and Goldman" #"the cat eats mice" #
    if sentence.startswith("*") or sentence.startswith("//") or sentence.isdigit() or sentence.startswith('(') or sentence.startswith('<'):
        print(sentence)
        continue
    print("//Input sentence: " + sentence)
    punct = "?" if "?" in sentence else "." 
    ret = invoke(cmd % sentence)
    matches = ret["matches"]
    entities = ret["entities"]
    names = {}
    lastindex = None
    print("//"+str(invoke(cmd % sentence)["matches"]))
    #2. retrieve KB nodes
    for entity in entities: #first, deal with the *c
        names[entity["id"]] = entity["name"]
    for match in matches:
        try:
            entity = match["entity"]
            cmd = """curl -X POST -H "Content-Type: application/json" -d '["%s" ]' http://localhost:8080/v2/knowledgegraph/entities"""
            ret = invoke(cmd % entity["id"])
            #2.1 Get categories:
            categories = ret["entities"][list(ret["entities"].keys())[0]]["categories"]
            #2.2 Build inheritance statements:
            subject = names[entity["id"]].replace(" ", "_").replace("(","_").replace(")","_")
            index = match["charOffset"]
            if lastindex != None and index < lastindex:
                subjects = subjects + [subject]
            else:
                subjects = [subject] + subjects
            lastindex = index
            for c in categories:
                predicate = (c.split("<")[1].split(">")[0] if "<" in c else c.split(":")[-1]).replace(" ", "_").replace("(","_").replace(")","_")
                if not predicate.startswith("wikicat_") and not predicate.startswith("wordnet_"): #for now to get only the few simple nodes
                    print("<" + subject + " --> " + predicate + ">.")
        except:
           None
    #Build verb relations:
    cmd = """curl --data '""" + sentence + """' 'http://localhost:9000/?properties={%22annotators%22%3A%22tokenize%2Cssplit%2Cpos%22%2C%22outputFormat%22%3A%22json%22}' -o -"""
    ret = invoke(cmd)
    for s in ret["sentences"]:
        for token in s["tokens"]:
            if token["pos"].startswith("VB") and len(subjects) > 0:
                relation = token["word"].upper()
                subjects_1 = subjects[1] if len(subjects) > 1 else subjects[0]
                subjects_0 = subjects[0] if len(subjects) > 1 else subjects[0]
                if punct == "?" and "what" in sentence or "who" in sentence:
                    if sentence.lower().startswith("what") or sentence.lower().startswith("who"):
                        subjects_1 = "?1"
                    else:
                        subjects_0 = "?1"
                if subjects_1 != None and len(subjects)>0:
                    if relation != "IS":
                        print("<(" + subjects_1 + " * " + subjects_0 + ") --> "+ relation + ">" + punct)
                    else:
                        print("<" + subjects_1 + " --> " + subjects_0 + ">" + punct)
        break
    sys.stdout.flush()
