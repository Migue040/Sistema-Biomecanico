%% pasar de posición a rotaciones en rad  %%

% INPUT coordenadas deseadas RANGO -0.4 a 0.4 (distancia indicada en m
% desde el centro del tablero

X = -.040;
Y = .22;

% r es el valor del radio de la polea conductora

r  = 0.020;
Simulation_Time = 5;

syms M1 M2

eqn1 = r/2*(M1+M2)==X;
eqn2 = r/2*(M1-M2)==Y;

sol = solve([eqn1, eqn2], [M1, M2]);
rad_M1 = double(sol.M1)
rad_M2 = double(sol.M2)



sim('sim_movement.slx',Simulation_Time);