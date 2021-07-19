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
    if sentence.startswith("*"):
        print(sentence)
        continue
    print("//Input sentence: " + sentence)
    punct = "?" if "?" in sentence else "." 
    entities = invoke(cmd % sentence)["entities"]
    #2. retrieve KB nodes
    for entity in entities:
        try:
            cmd = """curl -X POST -H "Content-Type: application/json" -d '["%s" ]' http://localhost:8080/v2/knowledgegraph/entities"""
            ret = invoke(cmd % entity["id"])
            #2.1 Get categories:
            categories = ret["entities"][list(ret["entities"].keys())[0]]["categories"]
            #2.2 Build inheritance statements:
            subject = entity["name"].replace(" ", "_").replace("(","_").replace(")","_")
            subjects.append(subject)
            for c in categories:
                predicate = (c.split("<")[1].split(">")[0] if "<" in c else c.split(":")[-1]).replace(" ", "_").replace("(","_").replace(")","_")
                print("<" + subject + " --> " + predicate + ">.")
        except:
            None
    #Build verb relations:
    cmd = """curl --data '""" + sentence + """' 'http://localhost:9000/?properties={%22annotators%22%3A%22tokenize%2Cssplit%2Cpos%22%2C%22outputFormat%22%3A%22json%22}' -o -"""
    ret = invoke(cmd)
    for sentence in ret["sentences"]:
        for token in sentence["tokens"]:
            if token["pos"].startswith("VB"):
                relation = token["word"].upper()
                subjects_1 = subjects[1] if len(subjects)>1 else ("?1" if punct == "?" else None) #questions support
                if subjects_1 != None and len(subjects)>0:
                    if relation != "IS":
                        print("<(" + subjects[0] + " * " + subjects_1 + ") --> "+ relation + ">" + punct)
                    else:
                        print("<" + subjects_1 + " --> " + subjects[0] + ">" + punct)
        break
    sys.stdout.flush()
