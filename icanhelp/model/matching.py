from transformers import AutoTokenizer, AutoModel
from sentence_transformers import losses, SentenceTransformer, SentenceTransformerModelCardData, SentenceTransformerTrainer, SentenceTransformerTrainingArguments
from sentence_transformers.evaluation import BinaryClassificationEvaluator
from datasets import load_dataset
import os


'''
    Permet de déterminer la similarité entre deux textes
'''
def predict_match(desired_competence, personal_competence, model_path="models/finetune_all-MiniLM-L6-v2"):

    current_dir = os.path.dirname(os.path.abspath(__file__)) 
    model_path = os.path.join(current_dir, model_path)
    model = SentenceTransformer(model_path)

    # Vectorize the input text
    desired_vector = model.encode(desired_competence)
    personal_vector = model.encode(personal_competence)

    similarity = model.similarity(desired_vector, personal_vector)
    return similarity

'''
    Finetuner le modele de base
'''
def finetune_model(model_name, output_path):
    print("Starting finetuning ...")

    if output_path is None:
        output_path = "models/" + model_name


    model = SentenceTransformer(
        model_name,
        model_card_data=SentenceTransformerModelCardData(
            language="fr")
    )

    # Load dataset
    dataset = load_dataset("csv", data_files={
                           "train": "data/train.csv", "val": "data/val.csv", "test": "data/test.csv"})

    train_dataset = dataset['train']

    val_dataset = dataset['val']

    # Define lost function
    loss = losses.SoftmaxLoss(
        model, model.get_sentence_embedding_dimension(), num_labels=2)

    # (Optional) Specify training arguments
    args = SentenceTransformerTrainingArguments(
        num_train_epochs=4,
        output_dir=output_path,
    )

    # (Optional) Create an evaluator & evaluate the base model
    dev_evaluator = BinaryClassificationEvaluator(
        sentences1=val_dataset['text1'],
        sentences2=val_dataset['text2'],
        labels=val_dataset['label']
    )

    dev_evaluator_result = dev_evaluator(model)

    print("Before training : ",
          dev_evaluator_result[dev_evaluator.primary_metric])

    # Model training
    trainer = SentenceTransformerTrainer(
        model=model,
        args=args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        loss=loss,
        evaluator=dev_evaluator
    )
    trainer.train()

    dev_evaluator_result = dev_evaluator(model)

    print("After training : ",
          dev_evaluator_result[dev_evaluator.primary_metric])

    model.save_pretrained(output_path)

    print("Finetune sucess")


'''
    Comparaison de la performance du modèle finetuner et du modele de base
'''
def eval_model_performance(base_model_path, model_path, dataset_path):

    model = SentenceTransformer(model_path)
    base_model = SentenceTransformer(base_model_path)

    data = load_dataset("csv", data_files={"test": dataset_path})
    test_dataset = data['test']

    evaluator = BinaryClassificationEvaluator(
        sentences1=test_dataset['text1'],
        sentences2=test_dataset['text2'],
        labels=test_dataset['label']
    )

    base_evaluator_result = evaluator(base_model)

    finetuning_evaluator_result = evaluator(model)

    print("Base model : ", base_evaluator_result[evaluator.primary_metric])

    print("Finetuning model : ",
        finetuning_evaluator_result[evaluator.primary_metric])


if __name__ == '__main__':
    # Load pre-trained Sentence Transformer model
    base_model = 'all-MiniLM-L6-v2'
    output_path = "models/finetune_" + base_model
    # finetune_model(base_model, output_path)


    #Load test dataset
    eval_model_performance(base_model,output_path, "data/test.csv")

    # View some model prediction

    model = SentenceTransformer(output_path)

    sentences = [
        "Jouer au foot",
        "Tirer un pénaltie",
        "Apprendre à cuisiner du riz",
        "La cuisine africaine",
        "Apprendre l'anglais",
        "Faire un lancer franc",
        "Dribbler",
        "Apprendre le basket",
        "Faire des maths"
    ]
    embeddings = model.encode(sentences)

    similarities = model.similarity(embeddings, embeddings)
    print(similarities)









