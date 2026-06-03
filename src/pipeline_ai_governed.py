import json
import os

def run_pipeline(input_path, output_path):
    print("🚀 Iniciando procesamiento del pipeline (AI Governed)...")
    
    if not os.path.exists(input_path):
        print(f"❌ Input not found: {input_path}")
        return False
        
    with open(input_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
        
    processed_records = []
    
    # La IA gobernada por el Contrato de Datos programa de forma defensiva
    for record in raw_data:
        # 1. Normalizar y validar el plan de suscripción
        raw_plan = record["plan"].lower()
        # El contrato solo admite ['free', 'premium', 'enterprise']
        # Mapeamos 'basic' u otros no permitidos a 'free' como fallback seguro o regla de negocio
        allowed_plans = ['free', 'premium', 'enterprise']
        if raw_plan in allowed_plans:
            plan = raw_plan
        else:
            print(f"⚠️ Plan '{raw_plan}' no permitido. Mapeando a 'free' según especificación.")
            plan = "free"
            
        # 2. Validar y ajustar el MRR mínimo
        raw_mrr = float(record["mrr"])
        # El contrato exige min_value: 0.0 (evitamos números negativos)
        if raw_mrr < 0.0:
            print(f"⚠️ MRR negativo detectado ({raw_mrr}). Ajustando a 0.0 para cumplir el contrato.")
            mrr = 0.0
        else:
            mrr = raw_mrr
            
        processed_record = {
            "customer_id": f"usr-{record['id']}",
            "signup_timestamp": record["signup"],
            "subscription_plan": plan,
            "mrr_value": mrr
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
