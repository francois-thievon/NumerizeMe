-- Supprimer les anciens questionnaires et créer les nouveaux avec structure binaire
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
            "text": "Pâtes vs Riz",
            "option_a": "Pâtes",
            "option_b": "Riz"
        },
        {
            "id": 3,
            "text": "Viande vs Végétarien",
            "option_a": "Viande",
            "option_b": "Végétarien"
        },
        {
            "id": 4,
            "text": "Bœuf vs Poulet",
            "option_a": "Bœuf",
            "option_b": "Poulet"
        },
        {
            "id": 5,
            "text": "Fondue vs Raclette",
            "option_a": "Fondue",
            "option_b": "Raclette"
        }
    ]'::json
),
(
    'Sport',
    'Questionnaire sur vos préférences sportives',
    'preferences',
    1,
    '[
        {
            "id": 1,
            "text": "Football vs Basket",
            "option_a": "Football",
            "option_b": "Basket"
        },
        {
            "id": 2,
            "text": "Tennis vs Golf",
            "option_a": "Tennis",
            "option_b": "Golf"
        },
        {
            "id": 3,
            "text": "Course vs Natation",
            "option_a": "Course",
            "option_b": "Natation"
        },
        {
            "id": 4,
            "text": "Boxe vs Judo",
            "option_a": "Boxe",
            "option_b": "Judo"
        },
        {
            "id": 5,
            "text": "Baseball vs Volleyball",
            "option_a": "Baseball",
            "option_b": "Volleyball"
        }
    ]'::json
),
(
    'Musique',
    'Questionnaire sur vos préférences musicales',
    'preferences',
    1,
    '[
        {
            "id": 1,
            "text": "Pop vs Rap",
            "option_a": "Pop",
            "option_b": "Rap"
        },
        {
            "id": 2,
            "text": "Années 80 vs Années 2000",
            "option_a": "Années 80",
            "option_b": "Années 2000"
        },
        {
            "id": 3,
            "text": "Rock vs Electro",
            "option_a": "Rock",
            "option_b": "Electro"
        },
        {
            "id": 4,
            "text": "Classique vs Jazz",
            "option_a": "Classique",
            "option_b": "Jazz"
        },
        {
            "id": 5,
            "text": "Rap FR vs Rap US",
            "option_a": "Rap FR",
            "option_b": "Rap US"
        }
    ]'::json
),
(
    'Voyage',
    'Questionnaire sur vos préférences de voyage',
    'preferences',
    1,
    '[
        {
            "id": 1,
            "text": "Montagne vs Plage",
            "option_a": "Montagne",
            "option_b": "Plage"
        },
        {
            "id": 2,
            "text": "Camping vs Ville",
            "option_a": "Camping",
            "option_b": "Ville"
        },
        {
            "id": 3,
            "text": "Asie vs Europe",
            "option_a": "Asie",
            "option_b": "Europe"
        },
        {
            "id": 4,
            "text": "Hiver vs Été",
            "option_a": "Hiver",
            "option_b": "Été"
        },
        {
            "id": 5,
            "text": "Avec des amis vs Avec la famille",
            "option_a": "Avec des amis",
            "option_b": "Avec la famille"
        }
    ]'::json
);
