-- Insertion des questionnaires avec la structure attendue par Pydantic
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
            "type": "single_choice",
            "text": "Hippopotame vs Crocodile",
            "options": ["Hippopotame", "Crocodile"],
            "min_scale": 1,
            "max_scale": 2
        },
        {
            "id": 2,
            "type": "single_choice", 
            "text": "Chien vs Chat",
            "options": ["Chien", "Chat"],
            "min_scale": 1,
            "max_scale": 2
        },
        {
            "id": 3,
            "type": "single_choice",
            "text": "Aigle vs Orque", 
            "options": ["Aigle", "Orque"],
            "min_scale": 1,
            "max_scale": 2
        },
        {
            "id": 4,
            "type": "single_choice",
            "text": "Lion vs Tigre",
            "options": ["Lion", "Tigre"],
            "min_scale": 1,
            "max_scale": 2
        },
        {
            "id": 5,
            "type": "single_choice",
            "text": "Lapin vs Hamster",
            "options": ["Lapin", "Hamster"],
            "min_scale": 1,
            "max_scale": 2
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
            "type": "single_choice",
            "text": "Pizza vs Sushis",
            "options": ["Pizza", "Sushis"],
            "min_scale": 1,
            "max_scale": 2
        },
        {
            "id": 2,
            "type": "single_choice",
            "text": "Pates vs Riz",
            "options": ["Pates", "Riz"],
            "min_scale": 1,
            "max_scale": 2
        },
        {
            "id": 3,
            "type": "single_choice",
            "text": "Viande vs Vege",
            "options": ["Viande", "Vege"],
            "min_scale": 1,
            "max_scale": 2
        },
        {
            "id": 4,
            "type": "single_choice",
            "text": "Boeuf vs Poulet",
            "options": ["Boeuf", "Poulet"],
            "min_scale": 1,
            "max_scale": 2
        },
        {
            "id": 5,
            "type": "single_choice",
            "text": "Fondue vs Raclette",
            "options": ["Fondue", "Raclette"],
            "min_scale": 1,
            "max_scale": 2
        }
    ]'::json
);
