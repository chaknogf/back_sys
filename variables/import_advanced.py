#!/usr/bin/env python3
"""
IMPORTADOR AVANZADO DE DATOS - EXCEL → PostgreSQL
Hospital General Tipo I de Tecpán Guatemala
Soporta 652 variables en 59 categorías

Uso:
    python3 import_advanced.py /ruta/al/2026.xlsx
    python3 import_advanced.py /ruta/al/2026.xlsx --host localhost --user postgres --password secret
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import sys
import argparse
import json
from datetime import datetime
from pathlib import Path

class AdvancedExcelImporter:
    def __init__(self, excel_path, db_host='localhost', db_user='postgres', 
                 db_password='postgres', db_name='transfusiones', db_port=5432, verbose=True):
        """Inicializar importador avanzado"""
        self.excel_path = excel_path
        self.verbose = verbose
        self.conn = None
        self.cursor = None
        self.stats = {
            'categories': 0,
            'variables_found': 0,
            'data_rows': 0,
            'records_inserted': 0,
            'errors': 0,
            'warnings': 0
        }
        
        try:
            self.conn = psycopg2.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                database=db_name,
                port=db_port
            )
            self.cursor = self.conn.cursor()
            self._log(f"✅ Conexión a PostgreSQL exitosa: {db_name}@{db_host}")
        except Exception as e:
            self._log(f"❌ Error de conexión: {e}", error=True)
            sys.exit(1)
    
    def _log(self, message, error=False, warning=False):
        """Registrar mensajes"""
        prefix = "❌" if error else ("⚠️ " if warning else "✅")
        if error:
            self.stats['errors'] += 1
        elif warning:
            self.stats['warnings'] += 1
        if self.verbose:
            print(f"{prefix} {message}")
    
    def read_excel(self):
        """Leer archivo Excel completo"""
        try:
            df = pd.read_excel(self.excel_path, sheet_name='Variables', header=None)
            self._log(f"Archivo Excel leído: {self.excel_path} ({df.shape[0]} filas × {df.shape[1]} columnas)")
            return df
        except Exception as e:
            self._log(f"Error al leer Excel: {e}", error=True)
            sys.exit(1)
    
    def extract_all_subsections(self, df):
        """Extraer TODAS las subsecciones (59 categorías) del archivo"""
        subsections = []
        
        for i in range(0, len(df)):
            col_c = df.iloc[i, 2]
            
            if pd.notna(col_c) and col_c == 'VARIABLES':
                # Subsección en fila anterior, columna B
                if i > 0:
                    subsection_name = df.iloc[i-1, 1]
                    if pd.isna(subsection_name):
                        subsection_name = df.iloc[i-1, 0]
                else:
                    subsection_name = "Sin Subsección"
                
                if pd.notna(subsection_name):
                    subsection_name = str(subsection_name).strip()
                    
                    # Extraer variables de la fila actual
                    variables = []
                    for col in range(3, len(df.columns)):
                        var = df.iloc[i, col]
                        if pd.notna(var) and isinstance(var, str):
                            var_str = var.strip()
                            if var_str and not var_str.startswith('='):
                                variables.append(var_str)
                    
                    if variables:
                        subsections.append({
                            'name': subsection_name,
                            'variables_row': i,
                            'variables': variables
                        })
                        self.stats['categories'] += 1
                        self.stats['variables_found'] += len(variables)
        
        self._log(f"Se encontraron {self.stats['categories']} categorías con {self.stats['variables_found']} variables")
        return subsections
    
    def extract_data_rows(self, df):
        """Extraer todas las filas de datos (meses)"""
        data_rows = {}
        
        for i in range(5, len(df)):
            month_cell = df.iloc[i, 2]
            if pd.notna(month_cell):
                month_str = str(month_cell).strip()
                if month_str in ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 
                                'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']:
                    if month_str not in data_rows:
                        data_rows[month_str] = []
                    data_rows[month_str].append(i)
        
        self.stats['data_rows'] = sum(len(v) for v in data_rows.values())
        self._log(f"Se encontraron datos para {len(data_rows)} meses ({self.stats['data_rows']} filas totales)")
        return data_rows
    
    def ensure_categories_in_db(self, subsections):
        """Asegurar que todas las categorías existan en la BD"""
        for subsection in subsections:
            cat_name = subsection['name'].replace("'", "''")
            
            self.cursor.execute(
                "SELECT category_id FROM variable_categories WHERE category_name = %s",
                (subsection['name'],)
            )
            
            if not self.cursor.fetchone():
                self.cursor.execute(
                    "INSERT INTO variable_categories (category_name, description) VALUES (%s, %s)",
                    (subsection['name'], f"{len(subsection['variables'])} variables")
                )
                self.conn.commit()
    
    def ensure_variables_in_db(self, subsections):
        """Asegurar que todas las variables existan en la BD"""
        for subsection in subsections:
            for var_name in subsection['variables']:
                var_code = ''.join([c for c in var_name if c.isalnum() or c == '_'])[:50]
                
                self.cursor.execute(
                    "SELECT variable_id FROM variables WHERE variable_code = %s",
                    (var_code,)
                )
                
                if not self.cursor.fetchone():
                    self.cursor.execute(
                        "SELECT category_id FROM variable_categories WHERE category_name = %s",
                        (subsection['name'],)
                    )
                    cat_id = self.cursor.fetchone()
                    
                    if cat_id:
                        self.cursor.execute(
                            "INSERT INTO variables (category_id, variable_name, variable_code, unit_of_measure, data_type) VALUES (%s, %s, %s, %s, %s)",
                            (cat_id[0], var_name, var_code, 'unidades', 'numeric')
                        )
                        self.conn.commit()
    
    def get_ids_from_db(self):
        """Obtener IDs de referencia de la BD"""
        try:
            # Hospital
            self.cursor.execute(
                "SELECT hospital_id FROM hospitals WHERE hospital_name = %s",
                ('Hospital General Tipo I de Tecpán Guatemala',)
            )
            hospital_id = self.cursor.fetchone()[0]
            
            # Departamento
            self.cursor.execute("SELECT department_id FROM departments LIMIT 1")
            department_id = self.cursor.fetchone()[0]
            
            # Meses
            self.cursor.execute("SELECT month_id, abbreviation FROM months ORDER BY month_number")
            months_dict = {row[1]: row[0] for row in self.cursor.fetchall()}
            
            # Géneros
            self.cursor.execute("SELECT gender_id, gender_name FROM genders")
            genders_dict = {row[1]: row[0] for row in self.cursor.fetchall()}
            
            # Variables
            self.cursor.execute("SELECT variable_id, variable_code FROM variables")
            variables_dict = {row[1]: row[0] for row in self.cursor.fetchall()}
            
            self._log(f"Referencias obtenidas: {len(variables_dict)} variables en BD")
            
            return {
                'hospital_id': hospital_id,
                'department_id': department_id,
                'months_dict': months_dict,
                'genders_dict': genders_dict,
                'variables_dict': variables_dict
            }
        except Exception as e:
            self._log(f"Error obteniendo IDs: {e}", error=True)
            sys.exit(1)
    
    def import_data(self, df, subsections, data_rows, ids_dict, year=2026):
        """Importar todos los datos del Excel"""
        records = []
        
        self._log(f"\n📊 Procesando datos para {year}...\n")
        
        for subsection in subsections:
            cat_name = subsection['name']
            var_row = subsection['variables_row']
            
            for var_idx, var_name in enumerate(subsection['variables']):
                var_code = ''.join([c for c in var_name if c.isalnum() or c == '_'])[:50]
                variable_id = ids_dict['variables_dict'].get(var_code)
                
                if not variable_id:
                    self._log(f"⚠️ Variable no encontrada: {var_name} ({var_code})", warning=True)
                    continue
                
                # Columna donde comienza esta variable (cada variable ocupa 3 columnas: M, F, T)
                col_start = 3 + (var_idx * 3)
                
                if col_start + 2 >= len(df.columns):
                    continue
                
                # Procesar cada mes
                for month_abbr, row_indices in data_rows.items():
                    month_id = ids_dict['months_dict'].get(month_abbr)
                    if not month_id:
                        continue
                    
                    # Para cada fila de datos de este mes
                    for data_row_idx in row_indices:
                        # Leer valores: masculino, femenino, total
                        male_val = df.iloc[data_row_idx, col_start]
                        female_val = df.iloc[data_row_idx, col_start + 1]
                        total_val = df.iloc[data_row_idx, col_start + 2]
                        
                        # Insertar masculino
                        if pd.notna(male_val) and male_val != '=+' and male_val != 0:
                            try:
                                male_val = float(male_val)
                                records.append((
                                    ids_dict['hospital_id'],
                                    ids_dict['department_id'],
                                    variable_id,
                                    month_id,
                                    ids_dict['genders_dict']['Masculino'],
                                    year,
                                    male_val,
                                    False
                                ))
                            except (ValueError, TypeError):
                                pass
                        
                        # Insertar femenino
                        if pd.notna(female_val) and female_val != '=+' and female_val != 0:
                            try:
                                female_val = float(female_val)
                                records.append((
                                    ids_dict['hospital_id'],
                                    ids_dict['department_id'],
                                    variable_id,
                                    month_id,
                                    ids_dict['genders_dict']['Femenino'],
                                    year,
                                    female_val,
                                    False
                                ))
                            except (ValueError, TypeError):
                                pass
                        
                        # Insertar total
                        if pd.notna(total_val) and total_val != '=+' and total_val != 0:
                            try:
                                total_val = float(total_val)
                                records.append((
                                    ids_dict['hospital_id'],
                                    ids_dict['department_id'],
                                    variable_id,
                                    month_id,
                                    ids_dict['genders_dict']['Total'],
                                    year,
                                    total_val,
                                    True  # is_calculated
                                ))
                            except (ValueError, TypeError):
                                pass
        
        # Insertar todos los registros
        self._log(f"\n💾 Insertando {len(records)} registros...\n")
        
        if records:
            try:
                sql = """
                INSERT INTO measurements 
                (hospital_id, department_id, variable_id, month_id, gender_id, year, measurement_value, is_calculated)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (hospital_id, department_id, variable_id, month_id, gender_id, year)
                DO UPDATE SET 
                    measurement_value = EXCLUDED.measurement_value,
                    is_calculated = EXCLUDED.is_calculated,
                    updated_at = CURRENT_TIMESTAMP
                """
                
                # Insertar en lotes de 1000
                batch_size = 1000
                for i in range(0, len(records), batch_size):
                    batch = records[i:i+batch_size]
                    execute_values(self.cursor, sql, batch)
                    self.conn.commit()
                    self._log(f"  Insertados {min(i + batch_size, len(records))}/{len(records)} registros")
                
                self.stats['records_inserted'] = len(records)
                self._log(f"✅ {len(records)} registros insertados exitosamente")
                return True
            except Exception as e:
                self.conn.rollback()
                self._log(f"Error insertando datos: {e}", error=True)
                return False
        else:
            self._log("⚠️ No se encontraron registros para insertar", warning=True)
            return False
    
    def validate_data(self, year):
        """Validar integridad de datos"""
        self._log("\n📋 Validando integridad de datos...\n")
        
        try:
            # Validar que total = masculino + femenino
            self.cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT m1.measurement_id
                FROM measurements m1
                WHERE m1.gender_id = (SELECT gender_id FROM genders WHERE gender_name = 'Total')
                AND m1.year = %s
                AND m1.measurement_value != COALESCE(
                    (SELECT measurement_value FROM measurements m WHERE 
                        m.variable_id = m1.variable_id 
                        AND m.month_id = m1.month_id 
                        AND m.gender_id = (SELECT gender_id FROM genders WHERE gender_name = 'Masculino')
                        AND m.hospital_id = m1.hospital_id 
                        AND m.department_id = m1.department_id 
                        AND m.year = m1.year), 0) +
                    COALESCE((SELECT measurement_value FROM measurements m WHERE 
                        m.variable_id = m1.variable_id 
                        AND m.month_id = m1.month_id 
                        AND m.gender_id = (SELECT gender_id FROM genders WHERE gender_name = 'Femenino')
                        AND m.hospital_id = m1.hospital_id 
                        AND m.department_id = m1.department_id 
                        AND m.year = m1.year), 0)
            ) as validation_errors
            """, (year,))
            
            errors = self.cursor.fetchone()[0]
            if errors == 0:
                self._log("✅ Validación exitosa: todos los totales son correctos")
                return True
            else:
                self._log(f"⚠️ Se encontraron {errors} inconsistencias en totales", warning=True)
                return False
        except Exception as e:
            self._log(f"Error en validación: {e}", error=True)
            return False
    
    def show_summary(self, year):
        """Mostrar resumen de importación"""
        self._log("\n" + "="*80)
        self._log("📊 RESUMEN DE IMPORTACIÓN")
        self._log("="*80)
        
        try:
            # Total de registros
            self.cursor.execute(
                "SELECT COUNT(*) FROM measurements WHERE year = %s",
                (year,)
            )
            total_records = self.cursor.fetchone()[0]
            self._log(f"\n📈 Total de registros: {total_records}")
            
            # Por categoría
            self.cursor.execute("""
            SELECT vc.category_name, COUNT(DISTINCT m.variable_id) as variables_con_datos, 
                   COUNT(*) as total_registros
            FROM measurements m
            JOIN variables v ON m.variable_id = v.variable_id
            JOIN variable_categories vc ON v.category_id = vc.category_id
            WHERE m.year = %s
            GROUP BY vc.category_id, vc.category_name
            ORDER BY total_registros DESC
            """, (year,))
            
            self._log("\n📋 Top 10 Categorías por registros:")
            for i, (cat_name, num_vars, num_records) in enumerate(self.cursor.fetchall()[:10], 1):
                self._log(f"   {i}. {cat_name}: {num_records} registros ({num_vars} variables)")
            
            # Por mes
            self.cursor.execute("""
            SELECT mo.month_name, COUNT(*) as registros
            FROM measurements m
            JOIN months mo ON m.month_id = mo.month_id
            WHERE m.year = %s
            GROUP BY mo.month_number, mo.month_name
            ORDER BY mo.month_number
            """, (year,))
            
            self._log("\n📅 Registros por mes:")
            for month_name, count in self.cursor.fetchall():
                self._log(f"   {month_name}: {count} registros")
            
            # Estadísticas generales
            self._log("\n📊 Estadísticas Generales:")
            self._log(f"   Categorías procesadas: {self.stats['categories']}")
            self._log(f"   Variables encontradas: {self.stats['variables_found']}")
            self._log(f"   Registros insertados: {self.stats['records_inserted']}")
            self._log(f"   Errores: {self.stats['errors']}")
            self._log(f"   Advertencias: {self.stats['warnings']}")
            
        except Exception as e:
            self._log(f"Error mostrando resumen: {e}", error=True)
    
    def close(self):
        """Cerrar conexión"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        self._log("\n✅ Conexión cerrada")
    
    def run(self, year=2026):
        """Ejecutar importación completa"""
        print("\n" + "="*80)
        print("🏥 IMPORTADOR AVANZADO DE DATOS")
        print("Hospital General Tipo I de Tecpán Guatemala")
        print("="*80 + "\n")
        
        # Paso 1: Leer Excel
        df = self.read_excel()
        
        # Paso 2: Extraer estructura
        self._log("\n📖 Extrayendo estructura del archivo...")
        subsections = self.extract_all_subsections(df)
        data_rows = self.extract_data_rows(df)
        
        # Paso 3: Garantizar categorías y variables
        self._log("\n🔧 Sincronizando categorías y variables con BD...")
        self.ensure_categories_in_db(subsections)
        self.ensure_variables_in_db(subsections)
        
        # Paso 4: Obtener IDs
        ids_dict = self.get_ids_from_db()
        
        # Paso 5: Importar datos
        success = self.import_data(df, subsections, data_rows, ids_dict, year)
        
        # Paso 6: Validar
        if success:
            self.validate_data(year)
        
        # Paso 7: Resumen
        self.show_summary(year)
        
        self.close()
        print("\n✅ Proceso completado\n")


def main():
    parser = argparse.ArgumentParser(
        description='Importador avanzado de datos - Excel a PostgreSQL (652 variables)'
    )
    parser.add_argument('excel_file', help='Ruta al archivo Excel')
    parser.add_argument('--host', default='localhost', help='Host PostgreSQL')
    parser.add_argument('--user', default='postgres', help='Usuario PostgreSQL')
    parser.add_argument('--password', default='postgres', help='Contraseña PostgreSQL')
    parser.add_argument('--database', default='transfusiones', help='Nombre de la BD')
    parser.add_argument('--port', type=int, default=5432, help='Puerto PostgreSQL')
    parser.add_argument('--year', type=int, default=2026, help='Año de los datos')
    parser.add_argument('--quiet', action='store_true', help='Modo silencioso')
    
    args = parser.parse_args()
    
    # Verificar que el archivo existe
    if not Path(args.excel_file).exists():
        print(f"❌ Error: Archivo no encontrado: {args.excel_file}")
        sys.exit(1)
    
    # Ejecutar importación
    importer = AdvancedExcelImporter(
        excel_path=args.excel_file,
        db_host=args.host,
        db_user=args.user,
        db_password=args.password,
        db_name=args.database,
        db_port=args.port,
        verbose=not args.quiet
    )
    
    importer.run(year=args.year)


if __name__ == '__main__':
    main()
