#Different functions to compare scansions

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def cosine_similarity(a, b):
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return dot_product / (norm_a * norm_b)

def compare_params(P1,P2):
    print(f"comparing {P1} and {P2}:")
    df1 = pd.read_csv(P1)
    df2 = pd.read_csv(P2)

    a = np.array(df1["p_long"])
    b = np.array(df2["p_long"])
    assert list(df1["syllable"] == list(df2["syllable"]))

    dl1 = np.sum(np.abs(np.array(a) - np.array(b)))
    dl2 = np.sqrt(np.sum((np.array(a) - np.array(b)) ** 2))
    dlinf = np.max(np.abs(np.array(a) - np.array(b)))
    dc1 = cosine_similarity(a,b)
    dc2 = cosine_similarity(a-0.5,b-0.5)


    print("L1 Distance:", dl1)
    print("L2 Distance:", dl2)
    print("L∞ Distance:", dlinf)
    print("Cosine Similarity:", dc1)
    print("Cosine Similarity 2:", dc2)

def compare_scansions(P1,P2):
    print(f"comparing scansions of {P1} and {P2}:")
    df1 = pd.read_csv(P1)
    df2 = pd.read_csv(P2)

    a = list(df1["assigned_pattern"])
    c1 = list(df1["confidence"])
    b = list(df2["assigned_pattern"])
    c2 = list(df2["confidence"])
    syllab = list(df1["verse_syllabified"])

    a = [i.replace("T","L") for i in a]
    b = [i.replace("T","L") for i in b]

    difference_indices = [i for i in range(len(a)) if a[i][:-1]!=b[i][:-1]]
    score = len(difference_indices)
    print(f"{score} scansions differ:")

    
    difference_sample=difference_indices[:10]
    for i in difference_sample:
        print(display_scansion(syllab[i],a[i]))
        print(display_scansion(syllab[i],b[i]))

    points= np.array([[c1[i],c2[i]] for i in difference_indices])
    
    plt.figure(figsize=(8, 8))
    plt.scatter(points[:, 0], points[:, 1], s=1, alpha=0.5, color='blue')
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.title("Scatterplot of confidences of disagreements")
    plt.grid(True, linestyle='--', alpha=0.7)

    # Show the plot
    plt.show()

def plot_confidences(path):
    df1 = pd.read_csv(path)
    
    values = list(df1["confidence"])
    print(f"mean confidence: {np.mean(values)}")
    plt.hist(values, bins=100, edgecolor='black', alpha=0.7)
    
    plt.show()


def display_scansion(syllabified,pattern):
    pattern = pattern.replace("-","")
    syllables = syllabified.split("|")
    result = []
    for (syl, c) in zip(syllables, pattern):
        if c=="T" or c=="L":
            result.append(syl.upper())
        else:
            result.append(syl)
    return "|".join(result)


def test_scansion(path,p2="test_set.csv"):
    df = pd.read_csv(path)
    df2 = pd.read_csv(p2)

    correct = list(df2["correct_pattern"])
    alternative = list(df2["alternative_pattern"])

    syllab = list(df["verse_syllabified"])
    
    scans = list(df["assigned_pattern"])
    scans = scans[:len(correct)]

    confs = list(df["confidence"])

    def patterns_agree(p1,p2):
        l1 = p1[:-1].replace("T","L")
        l2 = p2[:-1].replace("T","L")
        return l1==l2
        
    wrong = 0
    confidences=[]
    for i in range(len(scans)):
        if patterns_agree(scans[i],correct[i]):
            continue
        if type(alternative[i])==str:
            if patterns_agree(scans[i],alternative[i]):
                continue
        wrong+=1

        #print disagreeing lines
        print(display_scansion(syllab[i],scans[i]))
        print(display_scansion(syllab[i],correct[i]))
        
        confidences.append(confs[i])
    print(f"{wrong} wrong patterns in {len(correct)} verses")
    print(confidences)

test_scansion("../scansion/digbib_ilias_verses_with_scansion.csv")
