import json
import os

def run_pipeline(input_path, output_path):
    print("🚀 Iniciando procesamiento del pipeline (AI Ungoverned)...")
    
    if not os.path.exists(input_path):
        print(f"❌ Input not found: {input_path}")
        return False
        
    with open(input_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
        
    processed_records = []
    
    # La IA no gobernada asume conversiones directas sin validar contra la Spec de negocio
    for record in raw_data:
        processed_record = {
            "customer_id": f"usr-{record['id']}",
            "signup_timestamp": record["signup"],
            # Mapea directo a minúsculas, dejando pasar planes inválidos como 'basic'
            "subscription_plan": record["plan"].lower(),
            # Pasa el MRR directo, permitiendo valores negativos (refunds) que violan el contrato
            "mrr_value": float(record["mrr"])
        }
        processed_records.append(processed_record)
        
    # Guardamos los resultados
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_records, f, indent=2)
        
    print(f"✅ Pipeline finalizado. Resultados guardados en: {output_path}")
    return True

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    INPUT = os.path.join(script_dir, "../data/landing_raw.json")
    OUTPUT = os.path.join(script_dir, "../data/landing_processed.json")
    
    run_pipeline(INPUT, OUTPUT)
