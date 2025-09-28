-- Script pour créer des utilisateurs de test et tester le système de matching

-- Insérer des utilisateurs de test (mot de passe : "test123")
-- Hash bcrypt pour "test123": $2b$12$LKgO4YQJJEBXPtH6DJfDY.ZN9EQU3s4/5fUJLZKHhq9vVcpQKxEfG

INSERT INTO users (email, username, hashed_password, first_name, last_name, age, city, bio, is_active) VALUES
('alice@test.com', 'alice', '$2b$12$LKgO4YQJJEBXPtH6DJfDY.ZN9EQU3s4/5fUJLZKHhq9vVcpQKxEfG', 'Alice', 'Martin', 25, 'Paris', 'Aime les animaux et la nature', true),
('bob@test.com', 'bob', '$2b$12$LKgO4YQJJEBXPtH6DJfDY.ZN9EQU3s4/5fUJLZKHhq9vVcpQKxEfG', 'Bob', 'Dupont', 28, 'Lyon', 'Passionné de cuisine', true),
('claire@test.com', 'claire', '$2b$12$LKgO4YQJJEBXPtH6DJfDY.ZN9EQU3s4/5fUJLZKHhq9vVcpQKxEfG', 'Claire', 'Bernard', 23, 'Marseille', 'Adore voyager', true),
('david@test.com', 'david', '$2b$12$LKgO4YQJJEBXPtH6DJfDY.ZN9EQU3s4/5fUJLZKHhq9vVcpQKxEfG', 'David', 'Moreau', 30, 'Toulouse', 'Fan de musique et cinéma', true),
('emma@test.com', 'emma', '$2b$12$LKgO4YQJJEBXPtH6DJfDY.ZN9EQU3s4/5fUJLZKHhq9vVcpQKxEfG', 'Emma', 'Petit', 26, 'Nice', 'Sportive et aventurière', true);

-- Créer des réponses de test pour simuler des affinités
-- Alice (user_id: 5) répond aux questionnaires - aime les chats, la viande, etc.
INSERT INTO user_responses (user_id, questionnaire_id, answers) VALUES
(5, 13, '[
  {"question_id": 1, "choice": "b"},
  {"question_id": 2, "choice": "b"},
  {"question_id": 3, "choice": "a"},
  {"question_id": 4, "choice": "a"},
  {"question_id": 5, "choice": "a"}
]'),
(5, 14, '[
  {"question_id": 1, "choice": "a"},
  {"question_id": 2, "choice": "a"},
  {"question_id": 3, "choice": "a"},
  {"question_id": 4, "choice": "a"},
  {"question_id": 5, "choice": "a"}
]');

-- Bob (user_id: 6) répond aux questionnaires - préférences différentes d'Alice
INSERT INTO user_responses (user_id, questionnaire_id, answers) VALUES
(6, 13, '[
  {"question_id": 1, "choice": "a"},
  {"question_id": 2, "choice": "a"},
  {"question_id": 3, "choice": "b"},
  {"question_id": 4, "choice": "b"},
  {"question_id": 5, "choice": "b"}
]'),
(6, 14, '[
  {"question_id": 1, "choice": "b"},
  {"question_id": 2, "choice": "b"},
  {"question_id": 3, "choice": "b"},
  {"question_id": 4, "choice": "b"},
  {"question_id": 5, "choice": "b"}
]');

-- Claire (user_id: 7) répond aux questionnaires - préférences similaires à Alice
INSERT INTO user_responses (user_id, questionnaire_id, answers) VALUES
(7, 13, '[
  {"question_id": 1, "choice": "b"},
  {"question_id": 2, "choice": "b"},
  {"question_id": 3, "choice": "a"},
  {"question_id": 4, "choice": "a"},
  {"question_id": 5, "choice": "b"}
]'),
(7, 14, '[
  {"question_id": 1, "choice": "a"},
  {"question_id": 2, "choice": "a"},
  {"question_id": 3, "choice": "a"},
  {"question_id": 4, "choice": "b"},
  {"question_id": 5, "choice": "a"}
]');

-- David (user_id: 8) répond aux questionnaires - quelques similarités
INSERT INTO user_responses (user_id, questionnaire_id, answers) VALUES
(8, 13, '[
  {"question_id": 1, "choice": "a"},
  {"question_id": 2, "choice": "b"},
  {"question_id": 3, "choice": "a"},
  {"question_id": 4, "choice": "b"},
  {"question_id": 5, "choice": "a"}
]');

-- Emma (user_id: 9) répond aux questionnaires - mix de préférences
INSERT INTO user_responses (user_id, questionnaire_id, answers) VALUES
(9, 14, '[
  {"question_id": 1, "choice": "a"},
  {"question_id": 2, "choice": "b"},
  {"question_id": 3, "choice": "a"},
  {"question_id": 4, "choice": "a"},
  {"question_id": 5, "choice": "b"}
]');
