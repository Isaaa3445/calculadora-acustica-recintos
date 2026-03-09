import numpy as np
import matplotlib.pyplot as plt

# CONSTANTES FÍSICAS
c = 343.0            # velocidad del sonido en aire (m/s)
I0 = 1e-12           # intensidad acústica de referencia (W/m²)
W = 1e-3             # potencia acústica de la fuente (W)
Lw = 90.0            # nivel de potencia sonora de la fuente (dB)
Q = 2.0              # factor de directividad de la fuente
r = 2.0              # distancia entre fuente y receptor (m)
m = 0.003            # coeficiente de absorción del aire

# bandas de frecuencia usadas en acústica arquitectónica
frecuencias = np.array([125,250,500,1000,2000,4000])

# BASE DE DATOS DE MATERIALES
# coeficientes de absorción por banda de frecuencia
materiales = {

"concreto": [0.01,0.01,0.02,0.02,0.03,0.04],
"drywall": [0.05,0.05,0.05,0.04,0.07,0.09],
"ladrillo": [0.01,0.01,0.02,0.02,0.03,0.04],
"vidrio": [0.28,0.22,0.15,0.12,0.08,0.06],
"madera": [0.15,0.11,0.10,0.07,0.06,0.07],
"aluminio":[0.01,0.01,0.02,0.02,0.02,0.02],
"baldosa":[0.01,0.01,0.02,0.02,0.03,0.04]
    
}

# DIMENSIONES DEL RECINTO
# el usuario introduce dimensiones del recinto
largo = float(input("Largo del recinto (m): "))
ancho = float(input("Ancho del recinto (m): "))
alto = float(input("Altura del recinto (m): "))

# volumen del recinto
V = largo * ancho * alto

# cálculo de superficies
S_piso = largo * ancho
S_techo = S_piso

# superficie total de paredes
S_pared_total = 2*(largo*alto) + 2*(ancho*alto)

# superficie total del recinto
S_total = 2*S_piso + S_pared_total

# SELECCIÓN DE MATERIALES
# mostrar materiales disponibles
print("\nMateriales disponibles:")
for mtl in materiales:
    print("-",mtl)

# usuario selecciona material de piso y techo
piso = input("\nMaterial del piso: ")
techo = input("Material del techo: ")

# se obtienen coeficientes de absorción de la base de datos
alpha_piso = np.array(materiales[piso])
alpha_techo = np.array(materiales[techo])

# MATERIALES EN PAREDES
# permite usar varios materiales en paredes
n = int(input("\nNúmero de materiales en paredes: "))

# vector de absorción acumulada de paredes
A_pared = np.zeros(len(frecuencias))

for i in range(n):

    print("\nMaterial",i+1)

    mat = input("Nombre material: ")
    area = float(input("Área (m2): "))

    # coeficientes del material seleccionado
    alpha = np.array(materiales[mat])

    # absorción equivalente de esa sección
    A_pared += area * alpha

# ABSORCIÓN EQUIVALENTE
# absorción equivalente total del recinto
A = (S_piso*alpha_piso +
     S_techo*alpha_techo +
     A_pared)

# coeficiente de absorción promedio
alpha_prom = A / S_total

# TIEMPO DE REVERBERACIÓN
# fórmula de Sabine
RT_sabine = 0.161 * V / A

# fórmula de Eyring
RT_eyring = 0.161 * V / (-S_total * np.log(1-alpha_prom))

# fórmula de Millington
RT_millington = 0.161 * V / (
    -(S_piso*np.log(1-alpha_piso)
    + S_techo*np.log(1-alpha_techo)
    + A_pared*np.log(1-alpha_prom)/alpha_prom)
)


# RECORRIDO LIBRE MEDIO
# distancia promedio que recorre una onda entre reflexiones
l = 4*V / S_total


# REFLEXIONES
# número promedio de reflexiones del sonido
n_reflexiones = c * RT_sabine / l

# tiempo entre reflexiones
tau = l / c

# INTENSIDAD DE LA FUENTE
# intensidad directa de la fuente
If = W / (4*np.pi*r**2)

# nivel de intensidad sonora
LI = 10*np.log10(If/I0)

# CONSTANTE DE SALA
# constante de sala
R = A / (1-alpha_prom)


# CAMPO REVERBERADO
# intensidad del campo reverberado
Ir = 4*W / R

# NIVEL DE PRESIÓN SONORA TOTAL
# combinación campo directo + campo reverberado
Lp = Lw + 10*np.log10((Q/(4*np.pi*r**2)) + (4/R))

# DISTANCIA CRÍTICA
# distancia donde campo directo = campo reverberado
Dc = 0.057*np.sqrt(Q*R)

# =====================================
# ABSORCIÓN DEL AIRE
# =====================================

# nivel considerando atenuación por aire
Lp_r = Lp - 20*np.log10(r) - m*r

# RESULTADOS GENERALES
print("\n========== DATOS DEL RECINTO ==========")

print("Volumen del recinto:", round(V,2),"m3")
print("Superficie total:", round(S_total,2),"m2")
print("Recorrido libre medio:", round(l,3),"m")
print("Tiempo entre reflexiones:", round(tau,5),"s")

print("\nIntensidad acústica de la fuente:", round(If,8),"W/m2")
print("Nivel de intensidad:", round(LI,2),"dB")

print("\nConstante de sala por banda:")
print(np.round(R,3))

print("\nCampo reverberado por banda:")
print(np.round(Ir,8))

print("\nNivel presión sonora total:")
print(np.round(Lp,2))

print("\nDistancia crítica por banda:")
print(np.round(Dc,3))

print("\nNivel con absorción del aire:")
print(np.round(Lp_r,2))


# RESULTADOS POR BANDA
print("\n========== RESULTADOS POR BANDA ==========")

# imprimir resultados para cada banda de frecuencia
for i in range(len(frecuencias)):

    print("\nFrecuencia:",frecuencias[i],"Hz")

    print("RT Sabine:", round(RT_sabine[i],3),"s")
    print("RT Eyring:", round(RT_eyring[i],3),"s")
    print("RT Millington:", round(RT_millington[i],3),"s")

    print("Número promedio de reflexiones:", round(n_reflexiones[i],2))


# GRÁFICA
# gráfica comparativa de tiempos de reverberación
plt.plot(frecuencias,RT_sabine,'o-',label="Sabine")
plt.plot(frecuencias,RT_eyring,'s-',label="Eyring")
plt.plot(frecuencias,RT_millington,'^-',label="Millington")

plt.xlabel("Frecuencia (Hz)")
plt.ylabel("RT (s)")
plt.title("Tiempo de Reverberación vs Frecuencia")

plt.grid()
plt.legend()

plt.show()
