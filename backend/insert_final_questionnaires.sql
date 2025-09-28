-- Suppression des questionnaires existants et création des nouveaux questionnaires binaires
DELETE FROM questionnaires;

INSERT INTO questionnaires (title, description, category, weight, questions) VALUES
(
    'Animaux',
    'Questionnaire sur vos préférences d''animaux',
    'preferences',
    1,
    '[
        {
            "id": 1,
            "text": "Hippopotame vs Crocodile",
            "option_a": "Hippopotame",
            "option_b": "Crocodile"
        },
        {
            "id": 2,
            "text": "Chien vs Chat",
            "option_a": "Chien",
            "option_b": "Chat"
        },
        {
            "id": 3,
            "text": "Aigle vs Orque",
            "option_a": "Aigle",
            "option_b": "Orque"
        },
        {
            "id": 4,
            "text": "Lion vs Tigre",
            "option_a": "Lion",
            "option_b": "Tigre"
        },
        {
            "id": 5,
            "text": "Lapin vs Hamster",
            "option_a": "Lapin",
            "option_b": "Hamster"
        }
    ]'::json
),
(
    'Nourriture',
    'Questionnaire sur vos préférences alimentaires',
    'preferences',
    1,
    '[
        {
            "id": 1,
            "text": "Pizza vs Sushis",
            "option_a": "Pizza",
            "option_b": "Sushis"
        },
        {
            "id": 2,
            "text": "Pates vs Riz",
            "option_a": "Pates",
            "option_b": "Riz"
        },
        {
            "id": 3,
            "text": "Viande vs Vege",
            "option_a": "Viande",
            "option_b": "Vege"
        },
        {
            "id": 4,
            "text": "Boeuf vs Poulet",
            "option_a": "Boeuf",
            "option_b": "Poulet"
        },
        {
            "id": 5,
            "text": "Fondue vs Raclette",
            "option_a": "Fondue",
            "option_b": "Raclette"
        }
    ]'::json
);
