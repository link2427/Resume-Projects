#pragma once
#include "Player.h"

class BST {
private:
	Player* val;

	BST* right;
	BST* left;
public:
	void writePlayersData(BST* currentNode, std::ostream& outfile);
	~BST(); 
	BST();
	BST(Player *player);
	void insertPlayer(BST* currentNode, Player *player);
	int getCount(BST* currentNode); 
	void print(BST* currentNode); 
	double getTotalCaloriesBurned(); 
	void getPlayers(BST* currentNode, std::string inFileName); 
	void writeData(std::string outFileName, BST *players); 
	void free(BST* currentNode);
};