# Detecting Inconsistencies in the Modeling of SNOMED CT

**Author:** Emil Thomas Levin  
**Affiliation:** Department of Computer Science, Manhattan College, New York  
**Research Program:** KAKOS School of Science Summer Research  
**Advisor:** Dr. Ankur Agrawal  
**Date:** October 15, 2023

## Table of Contents
- [Introduction](#introduction)
- [Methodology](#methodology)
  - [The Similarity Algorithm](#the-similarity-algorithm)
- [Results](#results)
- [Discussion](#discussion)
- [Conclusion](#conclusion)
- [References](#references)

## Introduction

SNOMED CT or Systemized Nomenclature of Medicine Clinical Terms stands as the world's most sophisticated and clinically accepted healthcare terminology. Regulated by SNOMED International, this multilingual repository is currently the gold standard in over eighty nations, showcasing its global influence. Regular bi-annual updates ensure its content remains timely and relevant, catering to the ever-evolving world of medicine.

Boasting more than 350,000 active concepts organized meticulously across nineteen high-level hierarchies, SNOMED CT is unparalleled in its depth and breadth. Each concept encapsulates a clinical meaning, linked to descriptive, human-readable terms. These concepts also form intricate webs of relationships, be it hierarchical or attribute-based, ensuring a comprehensive representation of each medical term. 

To illustrate, consider figure 1 below: 


![Figure 1: Illustration of a concept in SNOMED CT](images/fig1.png)

The term "Myocardial infarction (disorder)" with its unique identifier 22298006 not only encompasses various descriptions like "Heart attack" but also intertwines with fourteen children concepts, four parent concepts, and intricate attribute relationships such as "Finding site” and “Associated morphology” linked to "Myocardium structure" and “Infarct.” 



However, with such vastness comes complexity. Inevitably, SNOMED CT is susceptible to inconsistencies, be it in the form of missing or incorrect relationships, attributes, or role groups. The literature is rich with studies that spotlight these inconsistencies, with methodologies varying from lexical feature analysis to tribal network abstraction networks [2-5]. Addressing these inconsistencies is paramount, making quality assurance a focal research area. Though manual audits offer precision, their laborious nature, as highlighted by Rector et al. [6], underscores the pressing need for automated, computational techniques to streamline the auditing process.

Building on prior research [8,9], this paper delves deeper into the fusion of sibling relationships and lexical techniques. Our intent is to magnify the precision in pinpointing inconsistencies while simultaneously reducing manual audit interventions. More than just identifying inconsistencies, our proposed method paints a comprehensive picture, offering contextual insights into modeling discrepancies. Beyond just quality assurance, our approach serves as a catalyst in uncovering inconsistencies in SNOMED CT concepts, thereby enriching its content.

To set the stage, let's delve into SNOMED CT, often touted as the "Google" for the medical community. In an era of relentless digital transformation, SNOMED CT stands tall as the universal language bridging the communication gap across healthcare systems worldwide.


## Methodology

The methodology outlined in this study is anchored in the July 2023 version of the International SNOMED CT. However, its design is versatile enough to be adaptable to other versions. At the core of our approach is the understanding that sibling concepts, which are lexically similar, should inherently display a congruency in their attribute modeling. This congruency pertains not only to the sheer number of attributes but also to the quality and nature of these attributes.

To elaborate, if we take two terms, say Term A and Term B, and categorize them as lexically similar, they should essentially mirror each other in their attribute composition. Any significant disparity in this attribute mapping indicates potential inconsistencies between the terms, which can have broader implications for the database's accuracy and utility.


Figure 2: Overall approach of methodology

The algorithm itself can be simplified in three main steps:

1. Sibling Concept Identification: The entirety of SNOMED CT's concepts are systematically paired. To qualify as a pair, two terms must exhibit a high degree of similarity — they must be of identical length and diverge by just a single word. An illustrative example of this criterion would be the pairing of the terms "Abnormality of right atrioventricular valve in double inlet ventricle (disorder)" and "Abnormality of left atrioventricular valve in double inlet ventricle (disorder)," where the only variation is the descriptors "right" and "left." From this vast pool, selections are made only for those pairs where both concepts have shared parents, thus deeming them as siblings.
  
2. Lexical Similarity Analysis: Using the word2vec algorithm, every sibling pair undergoes a lexical similarity test. A similarity score emerges from this process, with the metric spanning from 0 (complete dissimilarity) to 1 (absolute similarity). Our chosen threshold score is 0.9 to mark a pair as lexically similar.

3. Inconsistency Flagging: The final step scans for pairs where a disparity exists in the number of attribute relationships. Such pairs are flagged for inconsistencies and earmarked for a manual audit.


### The Similarity Algorithm

The crux of our approach lies in the algorithmic comparison of two SNOMED CT concept terms, yielding a similarity score reflective of their lexical resemblance. Utilizing word2vec—a two-layer neural network—our methodology harnesses the power of mapping words to distinct vectors. At its core, word2vec assimilates words to vectors based on context and relational analysis, ensuring that semantically similar terms correspond to similar vectors in a designated vector space.

Our corpus, a combination of PubMed and Wikipedia articles, feeds into this network. This rich corpus ensures that the generated vocabulary aligns well with SNOMED CT terminology and offers an accurate representation of inter-word relationships.


Figure 3: Overall approach of similarity calculation algorithm

Consider two concepts for comparison: Concept X and Concept Y (with the word count in X >= Y). After an initial preprocessing step where both concepts are converted to lowercase and devoid of their tags, each concept is broken down into individual words:

Concept X => [Z1, Z2, ..., Zn]

Concept Y => [z1, z2, ..., zm]

Each word from these concepts is transformed into its corresponding vector using our word2vec vocabulary, resulting in:

[Z1, Z2, ..., Zn] => [U1, U2, ..., Un]

[z1, z2, ..., zm] => [u1, u2, ..., um]

For both Concept X and Concept Y, we calculate the mean of their respective vector sets, yielding an average vector representation for each concept. With these average vector representations in hand for both concepts, we determine their similarity using Cosine similarity.  For words absent in the vocabulary, a score of 1 is assigned if the word appears in both concepts, otherwise, it gets a score of 0.

The final similarity score for the concept pair is the average of all individual word scores.


## Results

From the SNOMED CT database, we selected a random set of 50 terms from three distinct tags, disorder, procedure, and findings, culminating in a total of 150 terms. For these terms, our methodology successfully identified 70 sets of lexically similar terms, aggregating to 622 similar words as shown in Figure 4. This entails that for the 150 random input terms, almost half (70) had similar terms that could be grouped into sets.



Figure 4: Comparison of input terms to sets of similar terms found


Upon further assessment of these 70 sets for modeling inconsistencies, our approach flagged 20 sets as potentially inconsistent. Every single one of these 20 sets exhibited at least one attribute discrepancy when juxtaposed with their corresponding similar terms. This highlights potential areas of SNOMED CT that might benefit from manual auditing to ensure precision and consistency in modeling. The expectation is that these flagged sets contain attributes that are inconsistent and would warrant further scrutiny by experts.




Figure 5: Results of auditing


Figure 5 illustrates the ratio of terms for which we identified similar terms versus the total number of input terms, segmented by tag. Figure 5 contrasts the number of consistent versus inconsistent sets among the 70 sets, further stratified by tag.


## Discussion

The results emphasize the efficiency and reliability of our methodology in pinpointing inconsistencies within SNOMED CT's modeling. The algorithm offers a high probability of correctly identifying potential inconsistencies. 

One salient advantage of our approach is the contextual auditing capability. By contrasting similar concepts, potential discrepancies become discernible, enabling us to identify and rectify them effectively.


## Conclusion

In an era where SNOMED CT stands as an indispensable global standard for encoding healthcare data, the introduction of our computational method marks a significant stride in healthcare informatics. This technique efficiently pinpoints inconsistencies, drastically reducing the need for labor-intensive manual audits. Beyond mere error identification, our method provides a dual benefit by also revealing and addressing inconsistencies in SNOMED CT. Implementing such advanced quality assurance strategies is paramount in fortifying ongoing endeavors to uphold and enhance the content quality of SNOMED CT, ensuring its continued reliability and comprehensive utility in the healthcare domain.

## References

1. [word2vec Tools - Bio.nlplab.org](https://bio.nlplab.org/#word-vector-tools)
2. [SNOMED International](https://www.snomed.org)
3. Agrawal, Ankur, and Kashifuddin Qazi. “Quality Assurance of SNOMED CT Using Lexical Similarity and Sibling Relationships.” ICMHI  2023, Kyoto, Japan, May 12-14, 2023.
4. ...

