from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch

def get_model(model):
  """Loads model from Hugginface model hub"""
  try:
    model = AutoModelForTokenClassification.from_pretrained(model)
    model.save_pretrained('./model')
  except Exception as e:
    raise(e)

def get_tokenizer(tokenizer):
  """Loads tokenizer from Hugginface model hub"""
  try:
    tokenizer = AutoTokenizer.from_pretrained(tokenizer)
    tokenizer.save_pretrained('./model')
  except Exception as e:
    raise(e)

get_model('dslim/bert-base-NER')
get_tokenizer('dslim/bert-base-NER')