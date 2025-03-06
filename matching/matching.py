from sentence_transformers import SentenceTransformer
from sentence_transformers import util


sentences = ["Apprendre le piano", "Jouer au piano"]

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
#embeddings = model.encode(sentences)


while True:
    sentence1 = input("Sentence 1 : ")
    sentence2 = input("Sentence 2  " )

    embedding1 = model.encode(sentence1)
    embedding2 = model.encode(sentence2)


    sim = util.cos_sim(embedding1, embedding2 )

    print(sim)