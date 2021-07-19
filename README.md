# Channels
Sensory channels, knowledge channels and sensorimotor channels for OpenNARS

# NLPAndKnowledgeChannel.py example:

```
python3 NLPAndKnowledgeChannel.py | ./NAR shell
a cat is a mammal
Input: <Cat --> Mammal>. Priority=1.000000 Truth: frequency=1.000000, confidence=0.900000
what is a mammal?
Input: <?1 --> Mammal>?
Answer: <Cat --> Mammal>. Truth: frequency=1.000000, confidence=0.907493
Jack founded Alibaba
Input: <(Jack_Ma * Alibaba_Group) --> FOUNDED>. Priority=1.000000 Truth: frequency=1.000000, confidence=0.900000
Jack Ma founded what?
Input: <(Jack_Ma * ?1) --> FOUNDED>
Answer: <(Jack_Ma * Alibaba_Group) --> FOUNDED>. Truth: frequency=1.000000, confidence=0.900000
a cat is an animal
Input: <Cat --> Mammal>. Priority=1.000000 Truth: frequency=1.000000, confidence=0.900000
a mammal is an animal
Input: <Mammal --> Animal>. Priority=1.000000 Truth: frequency=1.000000, confidence=0.900000
a cat is an animal?
Input: <Cat --> Animal>?
Answer: <Cat --> Animal>. Truth: frequency=1.000000, confidence=0.460227
```
