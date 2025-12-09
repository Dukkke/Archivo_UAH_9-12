# -*- coding: utf-8 -*-
"""
Script EXPANDIDO para extraer categorías incluyendo:
- dc:subject (materias)
- dc:creator (autores/instituciones)
- dc:coverage (lugares)
- TIPOS: extraídos de títulos (Actas, Cartas, Oficios, etc.)
"""
import json
import re
from collections import Counter

def clean_text(text):
    """Limpia caracteres mal codificados"""
    replacements = {
        '\u00c3\u00a1': 'á', '\u00c3\u00a9': 'é', '\u00c3\u00ad': 'í', 
        '\u00c3\u00b3': 'ó', '\u00c3\u00ba': 'ú', '\u00c3\u00b1': 'ñ',
        '\u00c2': '', 'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 
        'Ãº': 'ú', 'Ã±': 'ñ'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.strip()

def extract_doc_type(title):
    """Extrae tipo de documento del título (busca palabras clave)"""
    title_lower = title.lower()
    
    # Lista de tipos de documentos a buscar
    doc_types = {
        'Acta': ['acta', 'actas'],
        'Carta': ['carta', 'cartas'],
        'Oficio': ['oficio', 'oficios'],
        'Informe': ['informe', 'informes'],
        'Memorándum': ['memorándum', 'memorandum', 'memo'],
        'Resolución': ['resolución', 'resolucion', 'resoluciones'],
        'Decreto': ['decreto', 'decretos'],
        'Fotografía': ['fotografía', 'fotografia', 'fotografías', 'foto', 'fotos'],
        'Discurso': ['discurso', 'discursos'],
        'Declaración': ['declaración', 'declaracion'],
        'Proyecto': ['proyecto', 'proyectos'],
        'Agenda': ['agenda', 'agendas'],
        'Minuta': ['minuta', 'minutas'],
        'Ley': ['ley ', 'leyes'],
        'Documento': ['documento', 'documentos'],
        'Solicitud': ['solicitud', 'solicita', 'solicitan'],
        'Respuesta': ['respuesta', 'respuestas'],
        'Invitación': ['invitación', 'invitacion'],
        'Comunicado': ['comunicado', 'comunicados'],
        'Telegrama': ['telegrama', 'telegramas'],
        'Volante': ['volante', 'volantes', 'panfleto'],
        'Partitura': ['partitura', 'partituras'],
        'Grabación': ['grabación', 'grabacion'],
    }
    
    found_types = []
    for doc_type, keywords in doc_types.items():
        for keyword in keywords:
            if keyword in title_lower:
                found_types.append(doc_type)
                break
    
    return found_types

def main():
    print("Cargando clean_with_metadata.json...")
    
    with open('clean_with_metadata.json', 'r', encoding='utf-8', errors='ignore') as f:
        data = json.load(f)
    
    print(f"Cargados {len(data)} documentos")
    
    # Colecciones para categorías únicas
    subjects = Counter()
    creators = Counter()
    coverages = Counter()
    doc_types = Counter()  # NUEVO: tipos de documentos
    
    for doc in data:
        # Extraer subjects (materias)
        for subject in doc.get('dc:subject', []):
            cleaned = clean_text(subject)
            if cleaned and len(cleaned) > 1:
                subjects[cleaned] += 1
        
        # Extraer creators (autores/instituciones)
        for creator in doc.get('dc:creator', []):
            cleaned = clean_text(creator)
            if cleaned and len(cleaned) > 1:
                creators[cleaned] += 1
        
        # Extraer coverage (lugares)
        for coverage in doc.get('dc:coverage', []):
            cleaned = clean_text(coverage)
            if cleaned and len(cleaned) > 1:
                coverages[cleaned] += 1
        
        # NUEVO: Extraer tipos de documento de títulos
        title = doc.get('title', '')
        types = extract_doc_type(title)
        for t in types:
            doc_types[t] += 1
    
    # Crear estructura de categorías COMPLETA
    categories = {
        "materias": [
            {"name": name, "count": count} 
            for name, count in subjects.most_common()
            if count >= 1
        ],
        "autores": [
            {"name": name, "count": count}
            for name, count in creators.most_common()
            if count >= 1
        ],
        "lugares": [
            {"name": name, "count": count}
            for name, count in coverages.most_common()
            if count >= 1
        ],
        "tipos": [
            {"name": name, "count": count}
            for name, count in doc_types.most_common()
            if count >= 1
        ]
    }
    
    # Guardar categorías
    with open('categories.json', 'w', encoding='utf-8') as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE CATEGORÍAS EXTRAÍDAS")
    print("="*60)
    
    print(f"\nMATERIAS (dc:subject): {len(categories['materias'])}")
    print(f"AUTORES (dc:creator): {len(categories['autores'])}")
    print(f"LUGARES (dc:coverage): {len(categories['lugares'])}")
    print(f"TIPOS (de títulos): {len(categories['tipos'])}")
    
    print("\n--- TIPOS DE DOCUMENTOS ---")
    for t in categories['tipos'][:15]:
        print(f"  {t['name']}: {t['count']}")
    
    total = sum(len(categories[k]) for k in categories)
    print(f"\nTOTAL CATEGORÍAS: {total}")
    
    print("\n" + "="*60)
    print("Categorías guardadas en: categories.json")
    print("="*60)

if __name__ == "__main__":
    main()
