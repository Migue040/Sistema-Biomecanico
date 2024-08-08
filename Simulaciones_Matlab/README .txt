README 

códigos Matlab proyecto Integrador


ControlMotor.slx - Muestra el lazo de control cerrado utilizado en los motores (solo simula el motor)

poleaSimple.slx - modelo de prueba para familiarizarse con los conceptos de bandas y poleas en Simulink

sim_movement.slx - modelo con simscape del robot con 12 grados de libertad, controlado por el sistema de control mostrado en ControlMotor, utiliza dos controladores de lazo cerrado.

coord.m - script para correr la simulación completa, se pueden dar los valores de la posición deseados como input

modeloRobot.slx - modelo multivariable del robot con valores proporcionales derivativos e integradores.

Sistema_Control.slx - modelo incorporando el ControlMotor y modeloRobot (malos resultados, requiere revisión)