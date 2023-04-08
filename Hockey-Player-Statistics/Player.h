#pragma once
#include <string>

class Player {
private:
	std::string fName;
	std::string lName;
	int stats[7];

public:
	Player();
	Player(std::string firstName, std::string lastName, int age,
		int shotsTargetFor, int shotsTargetAgainst, int missedShotsFor,
		int missedShotsAgainst, int met, int bodyWeight);
	std::string getFName(); 
	std::string getLName(); 
	int getStat(int index); 
	double getFenwick(); 
	double getCaloriesBurned(); 
	Player* next; 
	Player* previous; 
};