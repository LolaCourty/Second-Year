clear all
close all


% Construct a drivingScenario object.
Ts = 2; %sampling time
v = 1; %vitesse
scenario = drivingScenario('SampleTime', Ts);

% Récupération de données pour le cacul du taux de perte
t = [];
P1 = [];
P2 = [];
P3 = [];
P4 = [];

% Dimension d'un segment L
if rem(v,2) == 0    
    L=v*20;    
elseif v==1
    L = 20;
else
    L=(v-1)*20;
end

% Add all road segments
 for i=0:5
    for j=0:5 
        if j<5
            roadCenters = [i*L j*L 0 ;i*L (j+1)*L 0];
            laneSpecification = lanespec(1);
            road(scenario, roadCenters, 'Lanes', laneSpecification);
        end
        if i<5
            roadCenters = [i*L j*L 0 ;(i+1)*L j*L 0];
            laneSpecification = lanespec(1);
            road(scenario, roadCenters, 'Lanes', laneSpecification);
        end
    end
end

%add vehicle
Nb_car=20;      %nbre de voitures
Nb_car_ac = 2;  %Nbre de voitures au début, les autres seront ajoutés si la position initiale est libre
for i=1:2
    if rem(i,2) ~= 0        
        init_position = [0 0 0];
        point_passage(i,:) = [L 0 0];
        point_livraison(i,:) = [5*L 5*L 0];
        changement(i) = 0;
    else
       init_position = [0 5*L 0];
        point_passage(i,:) = [0 4*L 0]; %objectif intermédiaire
        point_livraison(i,:) = [5*L 0 0];
        changement(i) = 1;     %variable pour savoir s'il faut aller tout droit ou tourner
    end
    car(i) = vehicle(scenario, 'ClassID', 1, 'Position', init_position);
    speed(i)=v;  %vitesse    
    T0(i)=1+floor((i-1)/2)*Ts;  %date de départ de la voiture
    Livraison_OK(i)=0;      %1 = colis livré
    stop(i)=0;     %si stop=1 la voiture est à l'arret
    fin(i)=0;      %la voiture a fini son aller-retour
end
 
plot(scenario)  

while advance(scenario)
    %Récupération de données pour le calcul de taux de perte
    temps = scenario.SimulationTime;
    if (temps/Ts)
        [zone1, zone2, zone3, zone4] = liaison(car, Nb_car_ac, L);
        t= [t temps];
        P1 = [P1 zone1];
        P2 = [P2 zone2];
        P3 = [P3 zone3];
        P4 = [P4 zone4];  
    end
    %Ajout de voiture si la place est libre et qu'il faut encore en ajouter
    %
    nb = Nb_car_ac+1;
    if nb < Nb_car+1 && scenario.SimulationTime > T0(1)*42
        if car(nb-2).Position(2) <4*L + v*Ts  & rem(nb,2)==1
            [passage, livraison, chang, vehicule, init_position, temps_init] = new_car(scenario, 2, L);  
            point_passage(nb,:) = passage;
            point_livraison(nb,:)=livraison;
            car(nb) = vehicle(scenario, 'ClassID', 1, 'Position', init_position);
            speed(nb) = v;
            T0(nb) = temps_init;
            changement(nb) = chang;
            Livraison_OK(nb) = 0;
            stop(nb)=0;
            fin(nb) =0;
            nb=nb+1;
            Nb_car_ac = Nb_car_ac +1;
            %Ajout simultané si possible
            if car(nb-2).Position(1) > L - v*Ts & rem(nb,2)==0
                [passage, livraison, chang, vehicule, init_position, temps_init] = new_car(scenario, 1, L);
                point_passage(nb,:) = passage;
                point_livraison(nb,:)=livraison;
                car(nb) = vehicle(scenario, 'ClassID', 1, 'Position', init_position);
                speed(nb) = v;
                T0(nb) = T0(nb-1);
                changement(nb) = chang;
                Livraison_OK(nb) = 0;
                stop(nb)=0;
                fin(nb) =0;
                nb=nb+1;
                Nb_car_ac = Nb_car_ac +1;
            end
        elseif car(nb-2).Position(1) > L - v*Ts & rem(nb,2)==0
            [passage, livraison, chang, vehicule, init_position, temps_init] = new_car(scenario, 1, L);
            point_passage(nb,:) = passage;
            point_livraison(nb,:)=livraison;
            car(nb) = vehicle(scenario, 'ClassID', 1, 'Position', init_position);
            speed(nb) = v;
            T0(nb) = temps_init;
            changement(nb) = chang;
            Livraison_OK(nb) = 0;
            stop(nb)=0;
            fin(nb) =0;
            Nb_car_ac = Nb_car_ac +1;
        end
    end
    stop_prec = stop; %Pour savoir si la voiture est arrêtée depuis deux temps d'affilée
    for j=1:Nb_car_ac
        %detection des voitures
        flag_stop=zeros(1,Nb_car); %Distance de sécurité (3*v*Ts)
        flag_stop2=zeros(1,Nb_car); %Distance pour un arrêt d'urgence (collision)
        for i=1:Nb_car_ac
            if (i~=j) && (scenario.SimulationTime>T0(i)) && (scenario.SimulationTime>T0(j)) && (fin(i)==0) %on ne regarde que les voiture deja partie livrer
                scenario.SimulationTime;
                [zoneX,zoneY,flag_stop(i)] = distance(car(j),car(i), v, Ts);
                [zoneX2,zoneY2,flag_stop2(i)] = arret_urgent(car(j),car(i));
            end
        end
        %Si la voiture est arrêtée depuis plus d'un tour, elle essaie de
        %reculer pour débloquer la situation
        if max(flag_stop2) == 1 & stop_prec(j) == 1 & ~isequal(point_passage(j,:),[0 4*L 0]) & ~isequal(point_passage(j,:),[L 0 0])
                if ~inter && ~tourner
                    %La voiture recule pour laisser passer la voiture
                    %prioritaire qui la bloque 
                    [next_position, next_Yaw] = marche_arriere(car(j), changement(j), Livraison_OK(j), point_livraison(j,:), v, Ts, L);
                    car(j).Position=next_position;
                    car(j).Yaw=next_Yaw;
                %Si la voiture est en bout de grille, elle tourne
                elseif inter || tourner
                    car(j).Position=next_position;
                    car(j).Yaw=next_Yaw;
                    point_passage(j,:) = new_passage;
                end
        %Arrêt d'urgence sinon
        elseif max(flag_stop2) == 1 & ~isequal(point_passage(j,:),[0 0 0]) & ~isequal(point_passage(j,:),[0 5*L 0])
            stop(j)=1;
        else
            stop(j) = 0;
        end
        %Priorité aux voitures parties en premier
        if max(flag_stop(1:j))==1
            %La voiture ne doit pas s'arrêter au milieu d'une intersection
            if max(abs(car(j).Position-point_passage(j,:))) < 3*v*Ts + car(j).Length/2
                %Elle recule ou tourne selon sa localisation
                [inter, tourner, next_position, next_Yaw, new_passage] =retour_intersection(car(j), changement(j), Livraison_OK(j), point_livraison(j,:), point_passage(j,:),v, Ts, L);
                if ~inter && ~tourner
                    [next_position, next_Yaw] = marche_arriere(car(j), changement(j), Livraison_OK(j), point_livraison(j,:), v, Ts, L);
                    car(j).Position=next_position;
                    car(j).Yaw=next_Yaw;
                elseif inter || tourner
                    car(j).Position=next_position;
                    car(j).Yaw=next_Yaw;
                    point_passage(j,:) = new_passage;
                end
            %Si elle est au milieu d'une route et qu'une voiture s'approche, arrêt d'urgence ou recul    
            elseif ~isequal(point_passage(j,:),[0 4*L 0]) & ~isequal(point_passage(j,:),[L 0 0])
                for k=1:Nb_car_ac
                    if (k~=j) && (scenario.SimulationTime>T0(i)) && (scenario.SimulationTime>T0(j)) && (fin(k)==0)
                        [zoneX,zoneY,flag_stop(k)] = arret_urgent(car(j),car(k));
                        [inter, tourner, next_position, next_Yaw, new_passage] =retour_intersection(car(j), changement(j), Livraison_OK(j), point_livraison(j,:), point_passage(j,:),v, Ts, L);
                        if flag_stop(k) == 1 && ~inter && ~tourner
                            [next_position, next_Yaw] = marche_arriere(car(j), changement(j), Livraison_OK(j), point_livraison(j,:), v, Ts, L);
                            car(j).Position=next_position;
                            car(j).Yaw=next_Yaw;
                        elseif inter || tourner
                            car(j).Position=next_position;
                            car(j).Yaw=next_Yaw;
                            point_passage(j,:) = new_passage;
                        end
                    end
                end
            end
            stop(j)=1;
        end
                
        %deplacement des voitures
        if (scenario.SimulationTime>T0(j)) && (stop(j)==0) && (fin(j)~=1)
            [next_position, next_Yaw] = motion(car(j),point_passage(j,:),speed(j),Ts);
            car(j).Position=next_position;
            car(j).Yaw=next_Yaw;
            %On a atteint notre objectif intermédiaire
            if Livraison_OK(j)==0 & isequal(point_passage(j,:),car(j).Position)
                %On vise le suivant, ce qui implique de changer de
                %direction 
                changement(j) = (~changement(j));
                %Les voitures montent
                if changement(j) == 0
                    point_passage(j,:) = [point_passage(j,1)+L point_passage(j,2) 0];
                %Les voitures tournent à droite ou à gauche selon leur
                %point de départ
                else
                    if point_livraison(j,:) == [5*L 5*L 0]
                        point_passage(j,:) = [point_passage(j,1) (point_passage(j,2)+L) 0];
                    else
                        point_passage(j,:) = [point_passage(j,1) (point_passage(j,2)-L) 0];
                    end
                end
            end
            %Demi-tour
            if Livraison_OK(j)==1 & isequal(point_passage(j,:),car(j).Position)
                changement(j) = (~changement(j));
                %Les voitures descendent
                if changement(j) == 0
                    point_passage(j,:) = [point_passage(j,1)-L point_passage(j,2) 0];
                %Les voitures vont à droite ou à gauche selon leur point de
                %départ
                else
                    if point_livraison(j,:) == [0 L 0] | point_livraison(j,:) == [0 0 0]
                        point_passage(j,:) = [point_passage(j,1) (point_passage(j,2)-L) 0];
                    else
                        point_passage(j,:) = [point_passage(j,1) (point_passage(j,2)+L) 0];
                    end
                end
            end
        end
        %verification si point de livraison atteind ; si oui, la voiture repart au point de depart
        if car(j).Position==point_livraison(j,:)
            if Livraison_OK(j)==0
                Livraison_OK(j)=1;
                %On donne les nouvelles coordonnées pour retourner au point
                %de départ
                if isequal(point_livraison(j,:),[5*L 5*L 0])
                    point_passage(j,:) = [3*L 5*L 0];
                    point_livraison(j,:) = [0 L 0];
                else
                    point_passage(j,:) = [5*L 2*L 0];
                    point_livraison(j,:) = [L 5*L 0];
                end
            %Puisqu'il faut aller deux fois de suite dans la même
            %direction, on donne un point de livraison fictif, qu'on met
            %ici à jour
            elseif Livraison_OK(j)==1 & isequal(point_livraison(j,:),[0 L 0])
                point_livraison(j,:) = [0 0 0];
                point_passage(j,:) = [0 0 0];
                changement(j) = ~changement(j);
            elseif Livraison_OK(j)==1 & isequal(point_livraison(j,:),[L 5*L 0])
                point_livraison(j,:) = [0 5*L 0];
                point_passage(j,:) = [0 5*L 0];
                changement(j) = ~changement(j);
            else
                fin(j)=1;   %la voiture est revenue à son point de départ
            end
        end
    end
	updatePlots(scenario);
     pause(0.01);  %pour ralentir la simulation
end

%Fonction pour déterminer la nouvelle position et orientation des voitures
%pour les déplacer
function [next_Position next_Yaw] = motion(car,point_livraison,v,Ts)
        next_Position=car.Position;
        if car.Position(1)~= point_livraison(1)
            if abs(point_livraison(1)-car.Position(1))>v*Ts
                next_Position(1)=car.Position(1)+v*Ts*sign(point_livraison(1)-car.Position(1));
            else
                next_Position(1)=point_livraison(1);
            end
            if (point_livraison(1)-car.Position(1))>0 next_Yaw = 0;else next_Yaw = 180;end
        elseif car.Position(2)~= point_livraison(2)
            if abs(point_livraison(2)-car.Position(2))>v*Ts
                next_Position(2)=car.Position(2)+v*Ts*sign(point_livraison(2)-car.Position(2));
            else
                next_Position(2)=point_livraison(2);
            end
            if (point_livraison(2)-car.Position(2))>0 next_Yaw = 90;else next_Yaw = -90;end
        else
            next_Position=car.Position;
            next_Yaw=car.Yaw;
        end
end

%Fonction pour calculer la distance de sécurité
function [zoneX,zoneY,flag_stop] = distance(vehicle,vehicle_obstacle, v, Ts)
%zone devant le vehicule
if abs(rem(vehicle.Yaw,180))<2
    zoneX=sort(real([vehicle.Position(1) vehicle.Position(1)+exp(1j*pi*vehicle.Yaw/180)*3*vehicle.Length]));
    zoneY=sort(real([vehicle.Position(2)-2.5*v*Ts-vehicle.Length vehicle.Position(2)+2.5*v*Ts+vehicle.Length]));
else
    zoneX=sort(real([vehicle.Position(1)-2.5*v*Ts-vehicle.Length vehicle.Position(1)+2.5*v*Ts+vehicle.Length]));
    zoneY=sort(real([vehicle.Position(2) vehicle.Position(2)+exp(1j*pi*(vehicle.Yaw-90)/180)*3*vehicle.Length]));  
end  

%detection si obstacle dans la zone
if (vehicle_obstacle.Position(1)>zoneX(1)) && (vehicle_obstacle.Position(1)<zoneX(2)) && ...
   (vehicle_obstacle.Position(2)>zoneY(1)) && (vehicle_obstacle.Position(2)<zoneY(2))
     flag_stop =1;
else
     flag_stop =0;
end

end

%Fonction pour faire reculer les voitures
function [next_position, next_Yaw] = marche_arriere(car, chargement, Livraison_OK, point_livraison, v, Ts, L)
    position = car.Position;
    next_Yaw=car.Yaw;
    %On détermine par où elles allaient pour les faire reculer dans la
    %bonne direction
    if Livraison_OK == 0
        if chargement == 0
            next_position = [position(1)-2*v*Ts position(2) 0];
        else
            if isequal(point_livraison,[5*L 5*L 0])
                next_position = [position(1) position(2)-2*v*Ts 0];
            else
                next_position = [position(1) position(2)+2*v*Ts 0];
            end
        end
    else
        if chargement == 0
            next_position = [position(1)+2*v*Ts position(2) 0];
        else
            if point_livraison == [0 L 0] | point_livraison == [0 0 0]
                next_position = [position(1) position(2)+2*v*Ts 0];
            else
                next_position = [position(1) position(2)-2*v*Ts 0];
            end
        end
    end                   
end

%Fonction pour déterminer s'il risque d'y avoir collision
function [zoneX,zoneY,flag_stop] = arret_urgent(vehicle,vehicle_obstacle)
%zone devant le vehicule
if abs(rem(vehicle.Yaw,180))<2
    zoneX=sort(real([vehicle.Position(1) vehicle.Position(1)+ 0.6*exp(1j*pi*vehicle.Yaw/180)*3*vehicle.Length]));
    zoneY=sort(real([vehicle.Position(2)-vehicle.Length/2 vehicle.Position(2)+vehicle.Length/2]));
else
    zoneX=sort(real([vehicle.Position(1)-vehicle.Length/2 vehicle.Position(1)+vehicle.Length/2]));
    zoneY=sort(real([vehicle.Position(2) vehicle.Position(2)+0.6*exp(1j*pi*(vehicle.Yaw-90)/180)*3*vehicle.Length]));  
end  

%detection si obstacle dans la zone
if (vehicle_obstacle.Position(1)>zoneX(1)) && (vehicle_obstacle.Position(1)<zoneX(2)) && ...
   (vehicle_obstacle.Position(2)>zoneY(1)) && (vehicle_obstacle.Position(2)<zoneY(2))
     flag_stop =1;
else
     flag_stop =0;
end

end

%En bordure de grille, les voitures arrêtent de reculer et tournent
function [inter, tourner, next_position, next_Yaw, new_passage] = retour_intersection(car, chargement, Livraison_OK, point_livraison, point_passage, v, Ts, L)
    next_position = car.Position;
    position = car.Position;
    next_Yaw=car.Yaw;
    tourner = 0;
    inter = 0;
    new_passage = point_passage;
    %On détermine s'il faut tourner et si oui, dans quelle direction
    if Livraison_OK == 0
        if chargement == 0
            if point_passage(1)-position(1) > L 
                if position(1) < 1.5*v*Ts
                    tourner = 1;
                    if isequal(point_livraison,[5*L 5*L 0])
                        next_position = [0 position(2)-L/10 0];
                        next_Yaw = 90;
                    else
                        next_position = [0 position(2)+L/10 0];
                        next_Yaw = -90;
                    end
                else
                    tourner =0;
                end
            elseif point_passage(1)-position(1) > L + car.Length/2
                inter = 1;
            else
                inter = 0;
            end
        else
            if isequal(point_livraison,[5*L 5*L 0])
                if point_passage(2)-position(2) > L 
                    if position(2) < 1.5*v*Ts
                        tourner = 1;
                        next_position = [position(1)-L/10 0 0];
                        next_Yaw = 0;
                    else
                        tourner =0;
                    end
                elseif point_passage(2)-position(2) > L + car.Length/2
                    inter = 1;
                else
                    inter = 0;
                end
               
            else
                if position(2)-point_passage(2) > L
                    if position(2) > 5*L - 1.5*v*Ts
                        tourner = 1;
                        next_position = [position(1)-L/10 5*L 0];
                        next_Yaw = 0;
                    else
                        tourner =0;
                    end
                elseif position(2)-point_passage(2) > L + car.Length/2
                    inter = 1;
                else
                    inter = 0;
                end
            end
        end
    else
        if chargement == 0
            if position(1)- point_passage(1) > L 
                if position(2) > 5*L - 1.5*v*Ts
                    tourner = 1;
                    if point_livraison == [0 L 0] | point_livraison == [0 0 0]
                        next_position = [5*L position(2)-L/10 0];
                        next_Yaw = -90;
                    else
                        next_position = [5*L position(2)+L/10 0];
                        next_Yaw = 90;
                    end
                else
                    tourner =0;
                end  
            elseif position(1)-point_passage(1) > L + car.Length/2
                inter = 1;
            else
                inter = 0;
            end
        else
            if point_livraison == [0 L 0] | point_livraison == [0 0 0]
                if position(2) - point_passage(2) > L 
                    if position(2) > 5*L - 1.5*v*Ts
                        tourner = 1;
                        next_position = [position(1)+L/10 5*L 0];
                        next_Yaw = 180;
                    else
                        tourner =0;
                    end
                elseif position(2)-point_passage(2) > L + car.Length/2
                    inter = 1;
                else
                    inter = 0;
                end
            else
                if point_passage(2)-position(2) > L 
                    if position(2) < 1.5*v*Ts
                        tourner = 1;
                        next_position = [position(1)+L/10 0 0];
                        next_Yaw = 180;
                    else
                        tourner =0;
                    end
                elseif point_passage(2)-position(2) > L + car.Length/2
                    inter = 1;
                else
                    inter = 0;
                end                
            end
        end
    end  
end

%On ajoute une nouvelle voiture
function [passage, livraison, chang, vehicule, init_position, temps_init] = new_car(scenario, depart, L)
    if depart ==1
        init_position = [0 0 0];
        passage = [L 0 0];
        livraison = [5*L 5*L 0];
        chang = 0;
        vehicule = vehicle(scenario, 'ClassID', 1, 'Position', init_position);
        temps_init = scenario.SimulationTime;
    else
        init_position = [0 5*L 0];
        passage = [0 4*L 0];
        livraison = [5*L 0 0];
        chang = 1;
        vehicule = vehicle(scenario, 'ClassID', 1, 'Position', init_position);
        temps_init = scenario.SimulationTime;
    end
end

%On relève des données pour le calcul du taux de perte
function [zone1, zone2, zone3, zone4] = liaison(car, Nb_car_ac, L)
    zone1 = 0;
    zone2 = 0;
    zone3 = 0;
    zone4 = 0;
    for i=1:Nb_car_ac
        position = car(i).Position;
        if position(1) <= 3*L
            if position(2)<=3*L
                zone1 = zone1 +1;
            else
                zone2 = zone2 +1;
            end
        else
            if position(2)<=3*L
                zone3 = zone3 +1;
            else
                zone4 = zone4 +1;
            end
        end
    end
end

