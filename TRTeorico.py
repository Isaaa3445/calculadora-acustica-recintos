# Importamos las librerías necesarias
# numpy se usa para cálculos matemáticos
# matplotlib se usa para hacer la gráfica
import numpy as np
import matplotlib.pyplot as plt


# Bandas de frecuencia que se usarán en el análisis acústico
# Son bandas de octava típicas en acústica de recintos
freq = [125, 250, 500, 1000, 2000, 4000]


# Factor de directividad de la fuente
# Se fija en 2 porque se asume que la fuente está cerca de una pared
Q = 2


# ------------------------------------------------
# BASE DE DATOS DE MATERIALES ACÚSTICOS
# ------------------------------------------------
# Diccionario donde cada material tiene sus coeficientes
# de absorción para cada banda de frecuencia
materiales = {

"concreto":{125:0.01,250:0.01,500:0.02,1000:0.02,2000:0.02,4000:0.02},

"vidrio":{125:0.18,250:0.06,500:0.04,1000:0.03,2000:0.02,4000:0.02},

"madera":{125:0.15,250:0.11,500:0.10,1000:0.07,2000:0.06,4000:0.07},

"drywall":{125:0.29,250:0.10,500:0.05,1000:0.04,2000:0.07,4000:0.09},

"alfombra":{125:0.08,250:0.24,500:0.57,1000:0.69,2000:0.71,4000:0.73},

"panel_acustico":{125:0.25,250:0.60,500:0.90,1000:0.95,2000:0.95,4000:0.90},

"cortina":{125:0.10,250:0.35,500:0.55,1000:0.72,2000:0.70,4000:0.65},

"yeso":{125:0.02,250:0.02,500:0.03,1000:0.04,2000:0.05,4000:0.05},

"aluminio":{125:0.01,250:0.01,500:0.02,1000:0.02,2000:0.02,4000:0.02}

}


# ------------------------------------------------
# INGRESO DE DIMENSIONES DEL RECINTO
# ------------------------------------------------

# Se pide al usuario ingresar las dimensiones del recinto
largo = float(input("Largo del recinto (m): "))
ancho = float(input("Ancho del recinto (m): "))
alto = float(input("Altura del recinto (m): "))

# Se calcula el volumen del recinto
V = largo * ancho * alto


# ------------------------------------------------
# INGRESO DE MATERIALES DEL RECINTO
# ------------------------------------------------

# Se pregunta cuántos materiales hay en el recinto
n = int(input("¿Cuántos materiales tiene el recinto?: "))

# Listas donde se guardarán áreas y coeficientes
areas = []
coef = []

# Se muestran los materiales disponibles
print("\nMateriales disponibles:")
for m in materiales:
    print("-", m)


# Ciclo para ingresar cada material
for i in range(n):

    print("\nMaterial", i+1)

    # Área de la superficie que tiene ese material
    area = float(input("Área (m2): "))

    # Nombre del material
    nombre = input("Nombre del material: ")

    # Guardamos el área en la lista
    areas.append(area)

    # Guardamos los coeficientes del material
    coef.append(materiales[nombre])


# ------------------------------------------------
# CÁLCULO DE ABSORCIÓN POR BANDAS
# ------------------------------------------------

# Lista donde se almacenará la absorción equivalente
A = []

# Se recorre cada banda de frecuencia
for f in freq:

    suma = 0

    # Se suma área * coeficiente de absorción
    for i in range(n):
        suma += areas[i] * coef[i][f]

    # Se guarda el resultado
    A.append(suma)


# Área total del recinto
S = sum(areas)


# Coeficiente de absorción promedio
alpha_prom = [A[i] / S for i in range(len(freq))]


# ------------------------------------------------
# TIEMPO DE REVERBERACIÓN - SABINE
# ------------------------------------------------

RT_sabine = []

# Fórmula de Sabine
for a in A:
    RT_sabine.append(0.161 * V / a)


# ------------------------------------------------
# TIEMPO DE REVERBERACIÓN - EYRING
# ------------------------------------------------

RT_eyring = []

for alpha in alpha_prom:
    RT_eyring.append(0.161 * V / (-S * np.log(1 - alpha)))


# ------------------------------------------------
# TIEMPO DE REVERBERACIÓN - MILLINGTON
# ------------------------------------------------

RT_millington = []

for f in freq:

    suma = 0

    for i in range(n):

        alpha = coef[i][f]

        suma += areas[i] * np.log(1 - alpha)

    RT_millington.append(0.161 * V / (-suma))


# ------------------------------------------------
# DISTANCIA CRÍTICA
# ------------------------------------------------

Dc = []

# Se calcula para cada banda
for T in RT_sabine:
    Dc.append(0.057 * np.sqrt(Q * V / T))


# ------------------------------------------------
# IMPRESIÓN DE RESULTADOS
# ------------------------------------------------

print("\nRESULTADOS\n")

for i in range(len(freq)):

    print("Frecuencia:", freq[i], "Hz")

    print("Sabine:", round(RT_sabine[i], 2), "s")

    print("Eyring:", round(RT_eyring[i], 2), "s")

    print("Millington:", round(RT_millington[i], 2), "s")

    print("Distancia crítica:", round(Dc[i], 2), "m")

    print()


# ------------------------------------------------
# GRÁFICA DEL TIEMPO DE REVERBERACIÓN
# ------------------------------------------------

# Se grafican los resultados
plt.plot(freq, RT_sabine, 'o-', label="Sabine")

plt.plot(freq, RT_eyring, 's-', label="Eyring")

plt.plot(freq, RT_millington, '^-', label="Millington")

# Etiquetas de los ejes
plt.xlabel("Frecuencia (Hz)")
plt.ylabel("Tiempo de reverberación (s)")

# Título
plt.title("Tiempo de reverberación vs frecuencia")

# Cuadrícula
plt.grid(True)

# Leyenda
plt.legend()

# Mostrar la gráfica
plt.show()

c = 343

# Recorrido libre medio
l = 4*V/S

# Usamos RT a 500 Hz
T = RT_sabine[2]

# Numero promedio de reflexiones
N = c*T/l

# Tiempo entre reflexiones
t_ref = l/c

# Suposiciones para la fuente
W = 0.01
r = 2

# Intensidad acustica
I = W/(4*np.pi*r**2)

# Nivel de intensidad
LI = 10*np.log10(I/1e-12)

# Campo reverberado
Ir = 4*W/A[2]

# Constante de sala
R = A[2]/(1-alpha_prom[2])

# Nivel de potencia sonora
Lw = 10*np.log10(W/1e-12)

# Nivel de presion sonora total
Lp = Lw + 10*np.log10((Q/(4*np.pi*r**2)) + (4/R))

# Distancia critica
Dc = 0.057*np.sqrt(Q*V/T)

# Absorcion del aire
m = 0.001
A_aire = 4*m*V

print("\nPARAMETROS ACUSTICOS ADICIONALES\n")

print("Recorrido libre medio:",round(l,2),"m")
print("Numero promedio de reflexiones:",round(N,2))
print("Tiempo entre reflexiones:",round(t_ref,4),"s")
print("Intensidad acustica:",I,"W/m2")
print("Nivel de intensidad:",round(LI,2),"dB")
print("Campo reverberado:",round(Ir,6))
print("Constante de sala:",round(R,2))
print("Nivel de presion sonora total:",round(Lp,2),"dB")
print("Distancia critica:",round(Dc,2),"m")
print("Absorcion del aire:",round(A_aire,4))
