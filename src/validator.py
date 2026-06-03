import yaml
import json
import sys
import re
import os

def load_spec(spec_path):
    with open(spec_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def validate_file(data_path, spec):
    if not os.path.exists(data_path):
        print(f"❌ Archivo no encontrado: {data_path}")
        return False

    with open(data_path, 'r', encoding='utf-8') as f:
        try:
            records = json.load(f)
        except json.JSONDecodeError:
            print(f"❌ Error crítico: {data_path} no es un JSON válido o está vacío.")
            return False

    # Asegurar que records sea una lista para iteración
    if not isinstance(records, list):
        # Si es un solo objeto JSON, lo metemos en una lista
        records = [records]

    fields_spec = spec['fields']
    errors = []

    for index, row in enumerate(records):
        for field, rules in fields_spec.items():
            # 1. Validar requeridos
            if rules.get('required') and field not in row:
                errors.append(f"Fila {index}: Campo requerido '{field}' ausente.")
                continue
            
            if field in row:
                val = row[field]
                
                # 2. Validar tipo Float/Int
                if rules['type'] == 'float':
                    if not isinstance(val, (int, float)):
                        errors.append(f"Fila {index}: '{field}' debe ser float. Recibido: {type(val).__name__} ({val})")
                        continue
                    if 'min_value' in rules and val < rules['min_value']:
                        errors.append(f"Fila {index}: '{field}' viola el mínimo de {rules['min_value']}. Recibido: {val}")

                # 3. Validar tipo String y restricciones
                elif rules['type'] == 'string':
                    if not isinstance(val, str):
                        errors.append(f"Fila {index}: '{field}' debe ser string. Recibido: {type(val).__name__}")
                        continue
                    if 'allowed_values' in rules and val not in rules['allowed_values']:
                        errors.append(f"Fila {index}: '{field}' tiene un valor no permitido. Recibido: '{val}'")
                    if 'pattern' in rules and not re.match(rules['pattern'], val):
                        errors.append(f"Fila {index}: '{field}' no cumple el patrón regex '{rules['pattern']}'. Recibido: '{val}'")

    if errors:
        print(f"\n🚨 INCUMPLIMIENTO DE CONTRATO DETECTADO EN: {data_path}")
        for err in errors:
            print(f"   - {err}")
        return False
    
    print(f"✅ {data_path} cumple 100% con la especificación '{spec['dataset_name']}'.")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python src/validator.py <ruta_del_archivo_json> [ruta_del_contrato]")
        sys.exit(1)
        
    TARGET_DATA = sys.argv[1]
    
    # Resolver ruta de contrato por defecto relativa a este script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    DEFAULT_SPEC_PATH = os.path.join(script_dir, "../contracts/customer_v1.yaml")
    
    SPEC_PATH = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_SPEC_PATH
    
    if not os.path.exists(SPEC_PATH):
        print(f"❌ Especificación del contrato no encontrada en: {SPEC_PATH}")
        sys.exit(1)
        
    contract = load_spec(SPEC_PATH)
    
    if validate_file(TARGET_DATA, contract):
        sys.exit(0)  # Éxito para Git / CI
    else:
        sys.exit(1)  # Fallo / Bloqueo para Git / CI
