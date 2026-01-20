# 📋 CASOS DE PRUEBA - NUEVAS REGLAS DE TIEMPOS

## ✅ Cambios Implementados

### Configuración Backend:
- **Intervalo mínimo**: 10 minutos (antes: 8 horas)
- **Timeout de ciclo**: 18 horas (antes: 16 horas)
- **Cooldown anti-rebote**: 60 segundos (sin cambios)
- **Máximo entradas diarias**: 4 entradas por empleado por día (NUEVO)

### Configuración Frontend (Scanner):
- **Cooldown global**: 3 segundos entre cualquier detección (antes: 1 segundo)
- **Cooldown por empleado**: 30 segundos individual (NUEVO - antes era global)
- **Sistema inteligente**: Cada empleado tiene su propio temporizador de bloqueo

---

## 🧪 Casos de Prueba a Validar

### **CASO 1: Devolución por Retardo**
```
Escenario: Empleado llega tarde, supervisor lo devuelve

8:00 AM → Marca ENTRADA ✅
8:05 AM → Intenta SALIDA ❌ "Espera 5 min para marcar salida"
8:10 AM → Marca SALIDA ✅ "Hasta luego [Nombre]"

Resultado Esperado: Sistema permite salida después de 10 minutos
```

### **CASO 2: Error de Turno**
```
Escenario: Empleado se equivoca de horario/turno

7:00 AM → Marca ENTRADA ✅ (no era su turno)
7:12 AM → Marca SALIDA ✅ (>10 min, se permite)

Resultado Esperado: Sale sin problemas después de 10 minutos
```

### **CASO 3: Jornada Laboral Normal (8 horas)**
```
Escenario: Día de trabajo típico

8:00 AM → Marca ENTRADA ✅
4:00 PM → Marca SALIDA ✅ (8 horas exactas)

Resultado Esperado: Todo funciona como antes
```

### **CASO 4: Jornada Extendida (hasta 18h)**
```
Escenario: Turno nocturno o jornada doble

8:00 AM → Marca ENTRADA ✅
1:00 AM (día siguiente) → Marca SALIDA ✅ (17 horas, dentro de ventana)

Resultado Esperado: Sistema permite salida antes de 18 horas
```

### **CASO 5: Olvidó Marcar Salida - Auto Cierre**
```
Escenario: Empleado olvida marcar salida, viene al día siguiente

Lunes 8:00 AM → Marca ENTRADA ✅
[No marca salida]
Martes 3:00 PM → Escanea rostro ✅ Nueva ENTRADA (>18h, ciclo auto-cerrado)

Resultado Esperado: Sistema interpreta como nueva entrada
```

### **CASO 6: Intentos Rápidos (Anti-rebote)**
```
Escenario: Empleado marca múltiples veces por error

8:00 AM → Marca ENTRADA ✅
8:00:30 AM → Intenta nuevamente ✅ "Ya registraste tu entrada" (no guarda en BD)
8:01:30 AM → Intenta nuevamente ✅ "Ya registraste tu entrada" (cooldown 60s)

Resultado Esperado: Solo el primer registro se guarda
```

### **CASO 7: Salida-Entrada-Salida Mismo Día**
```
Escenario: Empleado sale y vuelve a entrar el mismo día

8:00 AM → ENTRADA ✅
12:00 PM → SALIDA ✅ (4 horas, pero >10 min)
1:00 PM → ENTRADA ✅ (regresa de comida)
6:00 PM → SALIDA ✅ (5 horas, >10 min)

Resultado Esperado: Múltiples ciclos en el mismo día
```

### **CASO 8: Límite Exacto de 18 Horas**
```
Escenario: Empleado marca exactamente en el límite

Lunes 8:00 AM → ENTRADA ✅
Martes 2:00 AM → SALIDA ✅ (exactamente 18 horas)
Martes 2:01 AM → Si escanea ✅ ENTRADA (>18h, nuevo ciclo)

Resultado Esperado: En el límite aún permite salida
```

---

## 🆕 CASOS NUEVOS - Cooldown Inteligente y Límite Diario

### **CASO 9: Fila de Empleados (Cooldown Inteligente)**
```
Escenario: Varios empleados llegan al mismo tiempo

8:00:00 → Juan escanea → "Bienvenido Juan" ✅
          [Juan bloqueado 30 segundos] 🔒
          [Sistema desbloqueado en 3 segundos] ⏱️

8:00:05 → María escanea → "Bienvenida María" ✅
          [María bloqueada 30 segundos] 🔒
          [Sistema desbloqueado en 3 segundos] ⏱️

8:00:10 → Pedro escanea → "Bienvenido Pedro" ✅
          [Pedro bloqueado 30 segundos] 🔒

8:00:15 → Juan intenta de nuevo → ❌ (ignorado, aún en cooldown)
8:00:31 → Juan escanea de nuevo → ✅ (cooldown cumplido)

Resultado Esperado: Empleados diferentes pueden escanear cada 3 segundos
```

### **CASO 10: Mismo Empleado Intenta Dos Veces**
```
Escenario: Empleado intenta escanear inmediatamente después

8:00:00 → Juan escanea → "Bienvenido Juan" ✅
8:00:05 → Juan intenta de nuevo → ❌ (ignorado por cooldown de 30s)
8:00:20 → Juan intenta de nuevo → ❌ (ignorado por cooldown de 30s)
8:00:35 → Juan escanea de nuevo → ✅ "Ya registraste tu entrada" (backend cooldown 60s)

Resultado Esperado: Frontend bloquea 30s, backend bloquea 60s desde el primer registro
```

### **CASO 11: Máximo 4 Entradas Diarias - Operación Normal**
```
Escenario: Empleado con turno doble + pausas

8:00 AM  → ENTRADA #1 ✅ (1/4)
12:00 PM → SALIDA

1:00 PM  → ENTRADA #2 ✅ (2/4) [Regreso de comida]
5:00 PM  → SALIDA

6:00 PM  → ENTRADA #3 ✅ (3/4) [Turno extra]
11:00 PM → SALIDA

11:30 PM → ENTRADA #4 ✅ (4/4) [Último turno permitido]
2:00 AM  → SALIDA

Resultado Esperado: Todas las entradas permitidas
```

### **CASO 12: Máximo 4 Entradas Diarias - Límite Alcanzado**
```
Escenario: Empleado intenta 5ta entrada en el mismo día

[... después del CASO 11 ...]

2:30 AM → ENTRADA #5 ❌ "❌ Máximo de entradas diarias alcanzado (4), Juan"

Resultado Esperado: Sistema rechaza la 5ta entrada del día
```

### **CASO 13: Cooldown Inteligente - Tres Empleados Consecutivos**
```
Escenario: Medir tiempos reales en fila

8:00:00 → Empleado A → ✅ "Bienvenido"
8:00:03 → Empleado B → ✅ "Bienvenida" (3s después, permitido)
8:00:06 → Empleado C → ✅ "Bienvenido" (3s después, permitido)
8:00:09 → Empleado D → ✅ "Bienvenida" (3s después, permitido)

Resultado Esperado: Flujo continuo, ~3 segundos por empleado
```

### **CASO 14: Máximo Diario - Reset a Medianoche**
```
Escenario: Contador se resetea cada día

Martes:
8:00 AM  → ENTRADA #1 ✅
12:00 PM → SALIDA
1:00 PM  → ENTRADA #2 ✅
5:00 PM  → SALIDA
6:00 PM  → ENTRADA #3 ✅
11:00 PM → SALIDA
11:30 PM → ENTRADA #4 ✅ (última del martes)

Miércoles:
8:00 AM → ENTRADA #1 ✅ (contador reseteado, nueva cuenta)

Resultado Esperado: Cada día tiene su propio límite de 4 entradas
```

---

## 🔧 Cómo Probar

### Opción 1: Pruebas Manuales con Timestamps
Para simular tiempos, puedes modificar temporalmente:
```python
# En attendance.py, línea ~60
# Cambiar:
time_diff = datetime.utcnow() - last_record.timestamp_utc

# Por (SOLO PARA TESTING):
# Simular 15 minutos después:
time_diff = timedelta(minutes=15)

# Simular 20 horas después:
time_diff = timedelta(hours=20)
```

### Opción 2: Pruebas con API Directa
```bash
# 1. Marcar entrada
curl -X POST http://localhost:8000/api/attendance/check-in \
  -F "file=@foto_empleado.jpg"

# 2. Esperar tiempo real o modificar BD manualmente
# 3. Marcar salida
curl -X POST http://localhost:8000/api/attendance/check-in \
  -F "file=@foto_empleado.jpg"
```

### Opción 3: Modificar Timestamp en BD (SQLite)
```sql
-- Ver último registro
SELECT * FROM attendance_records ORDER BY timestamp_utc DESC LIMIT 1;

-- Simular que fue hace 15 minutos
UPDATE attendance_records 
SET timestamp_utc = datetime('now', '-15 minutes'),
    local_time = datetime('now', '-15 minutes')
WHERE id = 'ID_DEL_REGISTRO';

-- Simular que fue hace 20 horas
UPDATE attendance_records 
SET timestamp_utc = datetime('now', '-20 hours'),
    local_time = datetime('now', '-20 hours')
WHERE id = 'ID_DEL_REGISTRO';
```

---

## ⚠️ Mensajes Esperados

| Situación | Mensaje del Sistema |
|-----------|---------------------|
| Entrada exitosa | "Bienvenido [Nombre]" |
| Salida exitosa | "Hasta luego [Nombre]" |
| Menos de 10 min desde entrada | "⏱️ Espera X min para marcar salida, [Nombre]" |
| Menos de 60 seg desde último registro (backend) | "✓ Ya registraste tu entrada/salida, [Nombre]" |
| Menos de 30 seg mismo empleado (frontend) | (Ignorado silenciosamente, no procesa) |
| Más de 18h desde entrada sin salida | Nueva "Bienvenido [Nombre]" (ciclo nuevo) |
| Máximo 4 entradas alcanzado | "❌ Máximo de entradas diarias alcanzado (4), [Nombre]" |

---

## 📊 Ventajas de las Nuevas Reglas

✅ **Flexibilidad Operacional**
- Permite devoluciones por retardo (10 min en lugar de 8h)
- Gestiona errores de turno sin bloqueos largos

✅ **Jornadas Extendidas**
- 18 horas permite turnos nocturnos completos
- Cubre casos de guardias extendidas

✅ **Auto-Recuperación**
- Sistema se auto-corrige después de 18h
- No requiere intervención manual si olvidan marcar salida

✅ **Seguridad Mantenida**
- Cooldown de 60 segundos evita duplicados
- Todas las validaciones en backend (no se puede evadir)

✅ **Flujo Eficiente en Fila (NUEVO)**
- Cooldown inteligente por empleado (30s individual)
- Cooldown global reducido (3s entre detecciones)
- Empleados diferentes pueden marcar cada 3 segundos
- Mismo empleado bloqueado 30 segundos (evita duplicados)

✅ **Control de Abusos (NUEVO)**
- Máximo 4 entradas por empleado por día
- Permite turnos dobles, pausas largas, emergencias
- Previene patrones erráticos o "jugar" con el sistema
- Contador se resetea diariamente a medianoche

---

## 🚨 Recordatorio Importante

Después de probar en desarrollo:
1. ✅ Verificar que todos los casos funcionan
2. ✅ Informar a supervisores sobre nueva regla de 10 minutos
3. ✅ Capacitar al personal sobre los cambios
4. ✅ Monitorear registros anómalos en los primeros días
5. ✅ Probar flujo de fila (varios empleados consecutivos)
6. ✅ Validar que el límite de 4 entradas diarias funciona correctamente

---

## 🎯 Resumen de Capas de Seguridad

### Frontend (Flutter Scanner):
1. **Cooldown global**: 3 segundos entre cualquier detección
2. **Cooldown por empleado**: 30 segundos individual
3. **Previene spam**: Bloquea detecciones mientras procesa

### Backend (Python API):
1. **Anti-rebote**: 60 segundos (retorna mensaje sin guardar duplicado)
2. **Intervalo mínimo**: 10 minutos entre ENTRADA → SALIDA
3. **Timeout de ciclo**: 18 horas antes de auto-cierre
4. **Máximo diario**: 4 entradas por empleado por día
5. **Validación facial**: Threshold de 0.5 para reconocimiento

**Total**: 5 capas de validación garantizan integridad de datos
