#include "Player.h"



//Default constructor
Player::Player() {
	fName = "";
	lName = "";
	next = nullptr;
	previous = nullptr;
	for (int i = 0; i < 7; i++) {
		stats[i] = 0;
	}
}



//Constructor that takes arguments
Player::Player(std::string firstName, std::string lastName, int age, int shotsTargetFor, int shotsTargetAgainst, int missedShotsFor, int missedShotsAgainst, int met, int bodyWeight) {
	fName = firstName;
	lName = lastName;
	next = nullptr;
	previous = nullptr;
	stats[0] = age;
	stats[1] = shotsTargetFor;
	stats[2] = shotsTargetAgainst;
	stats[3] = missedShotsFor;
	stats[4] = missedShotsAgainst;
	stats[5] = met;
	stats[6] = bodyWeight;
}



//Get first name
std::string Player::getFName() {
	return fName;
}



//Get last name
std::string Player::getLName() {
	return lName;
}



//Get statistics
int Player::getStat(int index) {
	return stats[index];
}



//Get fenwick
double Player::getFenwick() {
	double numerator = (double)stats[1] + (double)stats[3];
	double denominator = numerator - ((double)stats[2] + (double)stats[4]);

	return numerator / denominator;
}



//Get calories burned
double Player::getCaloriesBurned() {
	double result = ((double)stats[5] * (double)stats[6] * 3.5) / 200;
	return result;
}