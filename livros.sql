CREATE TABLE IF NOT EXISTS livros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT EXISTS,
    autor TEXT,
    categoria TEXT,
    ano_publicacao INTEGER,
    avaliacao TEXT, -- 'Sim', 'Não' ou 'Mais ou menos'
    resumo TEXT     -- Texto longo para as ~20 linhas
);