-- Suppression des questionnaires existants
DELETE FROM questionnaires;

-- Questionnaire Animaux
INSERT INTO questionnaires (title, description, category, questions, weight) VALUES (
  'Animaux', 
  'Choisissez vos animaux préférés', 
  'preferences', 
  '[
    {"question_text": "Hippopotame vs Crocodile", "option_a": "Hippopotame", "option_b": "Crocodile"},
    {"question_text": "Chien vs Chat", "option_a": "Chien", "option_b": "Chat"},
    {"question_text": "Aigle vs Orque", "option_a": "Aigle", "option_b": "Orque"},
    {"question_text": "Lion vs Tigre", "option_a": "Lion", "option_b": "Tigre"},
    {"question_text": "Lapin vs Hamster", "option_a": "Lapin", "option_b": "Hamster"}
  ]'::json, 
  1
);

-- Questionnaire Nourriture
INSERT INTO questionnaires (title, description, category, questions, weight) VALUES (
  'Nourriture', 
  'Choisissez vos aliments préférés', 
  'preferences', 
  '[
    {"question_text": "Pizza vs Sushis", "option_a": "Pizza", "option_b": "Sushis"},
    {"question_text": "Pates vs Riz", "option_a": "Pates", "option_b": "Riz"},
    {"question_text": "Viande vs Vege", "option_a": "Viande", "option_b": "Vege"},
    {"question_text": "Boeuf vs Poulet", "option_a": "Boeuf", "option_b": "Poulet"},
    {"question_text": "Fondue vs Raclette", "option_a": "Fondue", "option_b": "Raclette"}
  ]'::json, 
  1
);
