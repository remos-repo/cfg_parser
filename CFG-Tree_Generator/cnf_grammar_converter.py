"""
Remo Motsuenyane (40917525)
10/03/2026
CFG sentence parser
cnf-grammar converter takes a CFG grammar as a commandline argument and converts it to Chomsky-Noam Form
CNF grammar json is outputed and used as an input in the cky_recogniser.py
The cky_recogniser program parses the sentences into trees with the sentence file and output file path as command-line arguments
Gemini AI used for assisted debugging
"""
from pathlib import Path
import json
import re
import argparse as ap

def flatten_rule(key, rule, num):
    flatten_dict ={}
    num +=1
    nonterminal_list = rule.split() #split "A B C {D, E}" into [A, B, C]
    a, b = nonterminal_list[:2] #a=A, b=B
    var = f"X{num}"
    #x = f"{a} {b}" #A b / a B 
     #X1, X2, X3....
    #x_rule = f"{var} x"
    rep_rule = " ".join([var] + nonterminal_list[2:])
    x_rule = f"{a} {b}"
    if len(rep_rule.split()) <=2:
        flatten_dict[key]= [rep_rule]
        flatten_dict[var]= [x_rule]
        return flatten_dict, num
    else:
        result_dict, final_num = flatten_rule(key, rep_rule, num)
        # 2. Add the current step's logic to that dictionary
        result_dict[var] = [x_rule] 
        # 3. Pass the whole thing back up the chain
        return result_dict, final_num 
    
def convert_to_cnf(key, rule_list, grammar_dict, grammar, num): 
    key_list =[]
    xrule_dict={}
    remaining_list = []
    for rhs in rule_list: #goes through whole rule list of a singular key
        print(f"- {rhs}")
        star = re.search(r"(\w+)\*",rhs)
        
        if star and star.group(0) in rhs.split():
                    adj_list=rhs.split()
                    list_index = rhs.split().index(star.group())
        
                    adj_star = star.group(0).strip()
                    adj = star.group(1)

                    after_star = adj_list[list_index+1] 
                    adj_rule = f"{adj} {after_star}"

                    if adj_rule not in key_list:
                        key_list.append(adj_rule)

                    remaining_rhs = rhs.replace(adj_star.strip(), "").strip()
                    if len(remaining_rhs.split()) > 2:
                        # Pass the cleaned string directly to flatten
                        flattened_stuff, num = flatten_rule(key, remaining_rhs, num)
                        
                        # Merge the new X-rules and the rules for the current key
                        for k, v in flattened_stuff.items():
                            if k == key:
                                key_list.extend(v)
                            else:
                                xrule_dict[k] = v
                        num += (len(remaining_rhs.split()) - 2)
                    else:
                        # If it's just 1 or 2 words (like "N"), just add it
                        key_list.append(remaining_rhs)
                    
                    continue
        if rhs in grammar_dict[key]: #checks for rule in new grammar dict being built
             continue
        else:
            if rhs in grammar: #looks for unit productions in cfg (loll i hope) 
                #N -->   "N": ["dog", "cat", "man", "woman", "park", "city", "telescope"],
                new_rhs = grammar[rhs]
                key_list.extend(new_rhs)
                #this should be a list
            else:                    
                rhs_list = rhs.split()
                    
                if len(rhs_list) > 2:
                    #A --> B C D to X1 -->B C, A --> X1 D
                    new_rhs_dict, num= flatten_rule(key, rule=rhs, num=num)
                    for k, v in new_rhs_dict.items():
                        if k == key:
                            key_list.extend(v)
                        else:
                            xrule_dict[k] = v
                    num += (len(rhs_list) - 2)
                elif len(rhs_list)==1:
                        key_list.append(rhs)
                else:
                    if len(rhs_list)==2:
                        new_rhs= f"{rhs}"
                        key_list.append(new_rhs)
                     
    return key_list, xrule_dict, num    



#parse user-specified command line
parser = ap.ArgumentParser(description="Provide grammar, sentence file and outputfile, defalut n=2")
#add arguments to accept user corpus
parser.add_argument("-g","--grammar",required=True, type=str, help="User-specified grammar path")
args = parser.parse_args()
#create variables to contain argument values
input_grammar = args.grammar


new_rule_list = []
grammar_dict =  {}
number=0

try:
    with open(input_grammar, "r", encoding="utf-8") as file:
        grammar = json.load(file)
except FileNotFoundError:
    print("Error: The file 'data.json' was not found.")


for key in grammar:
     grammar_dict[key]=[] #initialize all keys in dict

#iterate through the dictionary's key-value pairs
for key, rule_list in grammar.items():
        #if key not in grammar_dict:
            
            print(f"Key: {key}, List contents:")
            #new rules is key_list returned with list of flattened rules, 
            #new_xrules returns list of X{num} rules
            #number to globally update count for X{num}

            new_rules, new_xrules, number = convert_to_cnf(key, rule_list, grammar_dict, grammar, num=number)
            
            grammar_dict.update(new_xrules)

            for rule in new_rules:
                if rule not in grammar_dict:
                    grammar_dict[key].append(rule)
        
with open("cnf_grammar.json", 'w') as json_file:
    json.dump(grammar_dict, json_file, indent=4)
            

            


#print(grammar)
#each value has a list of diff rules in the key that make the values, so it needs to be nested i think

