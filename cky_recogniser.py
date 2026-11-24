"""
Remo Motsuenyane (40917525)
10/03/2026
CFG sentence parser
cnf-grammar converter takes a CFG grammar as a commandline argument and converts it to Chomsky-Noam Form
CNF grammar json is outputed and used as an input in the cky_recogniser.py
The cky_recogniser program parses the sentences into trees with the sentence file and output file path as command-line arguments
Gemini AI used for assisted debugging
generate_trees function Gemini generated with manual debugging
"""

from pathlib import Path
import json
import re
import argparse as ap

def generate_trees(nt, i, j, table):
    #recursively generates trees from lists of lists
    #initialise list to contain all possible parses
    
    all_trees = []
    derivations = table[i][j].get(nt, [])

    derivations = table[i][j].get(nt, [])

    for entry in derivations:

        #entry can be string -- terminal, or tuple containing k=split point, B + C, left and right child
        if isinstance(entry, str):
            #append non-terminal and word
            all_trees.append([nt, entry])
        
        elif isinstance(entry, tuple):
            k, B, C = entry #release variables from the tuples

            # Recursively get all possible subtrees for the left and right children
            left_subtrees = generate_trees(B, i, k, table)
            right_subtrees = generate_trees(C, k, j, table)
            
            # Combine every possible left child with every possible right child
            for left in left_subtrees:
                for right in right_subtrees:
                    # Format: ["S", [NP...], [VP...]]
                    all_trees.append([nt, left, right])
                    
    return all_trees

def cky_recognizer(words, grammar_dict): 
    n= len(words)
    table = [[{} for _ in range(n + 1)] for _ in range(n + 1)]

    #fill the superdiagonal with parts-of-speech
    for j in range(1, n+1):
        word = words[j-1]
        
         #find all instance of word in grammar dict
        for nonterminal, terminal in grammar_dict.items():
           
           if word in terminal:
              #check every assignment on if it can combine
              table[j-1][j].setdefault(nonterminal, []).append(word)
        #word_pos[word]= diagonal_pos

    #new loop to fill in from the left bottom up
    for j in range(2, n + 1):
        for i in range(j-2, -1, -1): #fencepost before j, 3rd argument to count back
            for k in range(i+1, j): #split [i, j] into i <k <j

                #b_parse, c_parse to store back pointers
                for B, B_parse in table[i][k].items(): #loop through all parts of speech in cell
                    for C, C_parse in table[k][j].items(): #loop through all parts of speech and compare with B cell
                        #look for A(nonterminal) -->BC
                        rule = f"{B} {C}"
                        for nonterminal, rules in grammar_dict.items():
                            if rule in rules:
                            # Store the components used for this parse
                            # (Split point k, Left child B, Right child C)
                                table[i][j].setdefault(nonterminal, []).append((k, B, C))

    start_symbol = 'S' 
    #find S symbol in [0,n]
    if start_symbol in table[0][n]:
        # Generate and return the list of all possible parse trees
        return generate_trees(start_symbol, 0, n, table)
    else:
        # Return the exact string required by your prompt
        return "No possible parse"
       

parser = ap.ArgumentParser(description="Provide grammar, sentence file and outputfile, defalut n=2") 
parser.add_argument("-s", "--sentences", required=True, type=str, help="User-specified sentence path ")
parser.add_argument("-o", "--output", required=True, type=str, help="provide output file path and name")
args = parser.parse_args()
sentence_file = args.sentences
output_file = args.output
cnf_grammar = Path("./cnf_grammar.json")


final_trees =[]
try:

    #read sentence.txt, read line one at a time, save sentence as list of words
    with open(sentence_file, "r", encoding="utf-8") as file:
        for line in file:
            words = line.strip().lower().split() 
            #find word in vocab, assign it a POS, find matching constituents
            parsed=cky_recognizer(words, cnf_grammar)
            final_trees.append({line: parsed})
except FileNotFoundError:
    print("Error: The file 'sentence file' was not found.")

     
with open(output_file, 'w', encoding="utf-8") as json_file:
    for tree in final_trees:
        json.dump(tree, json_file, indent=4)


