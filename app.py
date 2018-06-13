#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This script exposes an endpoint that takes GET requests, parses out a vector from the query string, named answers, and uses
# it as input in a series of operations to measure its affinity to each of the 2018 mexican elections candidate.
from flask import Flask, request, jsonify
from flask_cors import CORS
import operator

app= Flask(__name__)
CORS(app)

# candidatesVectors holds information regarding the stance of each candidate towards each of the 40 statements.
# For example, given a candidate's associated list, the element at index 0 corresponds with the 1st statement
# presented to the user, element 1 of the list corresponds to statement 2, and so on.
# The value of each element in the list ranges from 1 to 5, where 1 denotes STRONGLY AGREE and 5 STRONGLY DISAGREE.

# Because a user's list, taken from the request's query string, will be similarly composed, we can contrast their
# opinions from those found in the public policies of the candidates, thus being able to determine a measure of
# affinity to each of them
candidatesVectors = {
  'Andres Manuel Lopez Obrador':    [1,4,5,1,1,1,1,2,2,1,3,5,1,1,1,5,2,1,1,5,2,4,1,5,4,5,5,4,4,1,4,4,2,2,1,1,4,3,4,1,],
  'Ricardo Anaya':  [1,2,1,1,5,2,5,5,2,2,4,5,2,5,4,1,1,2,5,4,1,2,2,5,2,1,1,2,2,1,2,2,1,1,5,5,1,4,4,5,],
  'Jose Antonio Meade': [2,4,2,5,5,2,4,5,1,5,5,5,2,5,2,1,2,4,5,4,1,5,5,4,1,2,5,1,2,2,1,2,1,1,4,5,1,4,4,5,],
#   'Margarita Zavala':   [1,4,4,4,5,1,2,5,1,5,4,5,4,5,4,1,2,4,5,5,1,1,4,3,1,4,5,1,1,1,2,5,1,1,4,4,2,1,1,2,],
  'Jaime Rodriguez':    [5,1,4,4,5,2,4,4,1,4,5,1,2,5,5,1,2,2,4,5,1,5,4,1,2,2,5,4,5,2,2,2,2,1,5,2,1,1,1,2,],
}

# ChoicesMatrix is a 3-Dimensional matrix, composed of 40 individual 2-D matrices (one per statement),
# that stores the numerical meaning (how much should each candidate's affinity rise or fall) of each possible match
# between a users' answer (rows) and the corresponding 'answer', or viewpoint, of each candidate (columns).

# For example, if the user strongly agrees to statement 1, about say, state directed welfare systems,
# and a given a candidate strongly opposes welfare systems, we would enter the first matrix (index 0),
# corresponding to the first statement, to access the space of all of its possible permutations.
# Now, because the user chose STRONGLY AGREE, encoded as 1, we are to enter the first row (beware the actual
# index would be 0, not 1, since lists are zero-indexed).
# Then, to find our match, consider that because the candidate STRONGLY DISAGREEs to the statement, meaning 5,
# we are to lookup the fifth element of that particular row (again, because of zero-indexing, the index would be 4)
# This would give us a numerical value, i.e. -0.735, to be added to that particular candidate's affinity measure

choicesMatrix = [	[
		[0.735, 0.588, 0, -0.588, -0.735],
		[0.588, 0.588, 0, -0.588, -0.588],
		[-1.1025, -1.1025, 0, -1.1025, -1.1025],
		[-0.588, -0.588, 0, 0.588, 0.588],
		[-0.735, -0.588, 0, 0.588, 0.735],
									],
                  [
		[0.8214, 0.6571, 0, -0.6571, -0.8214],
		[0.6571, 0.6571, 0, -0.6571, -0.6571],
		[-1.2314, -1.2314, 0, -1.2314, -1.2314],
		[0.6571, -0.6571, 0, 0.6571, 0.6571],
		[-0.8214, -0.6571, 0, 0.6571, 0.8214],
									],
                  [
		[0.8157, 0.6525, 0, -0.6525, -0.8157],
		[0.6525, 0.6525, 0, -0.6525, -0.6525],
		[-1.2228, -1.2228, 0, -1.2228, -1.2228],
		[-0.6525, -0.6525, 0, 0.6525, 0.6525],
		[-0.8157, -0.6525, 0, 0.6525, 0.8157],
									],
                   [
		[1.136, 0.9088, 0, -0.9088, -1.136],
		[0.9088, 0.9088, 0, -0.9088, -0.9088],
		[-1.7040, -1.7040, 0, -1.7040, -1.7040],
		[-0.9088, -0.9088, 0, 0.9088, 0.9088],
		[-1.136, -0.9088, 0, 0.9088, 1.136],
									],
                   [
		[1.136, 0.9088, 0, -0.9088, -1.136],
		[0.9088, 0.9088, 0, -0.9088, -0.9088],
		[-1.7040, -1.7040, 0, -1.7040, -1.7040],
		[-0.9088, -0.9088, 0, 0.9088, 0.9088],
		[-1.136, -0.9088, 0, 0.9088, 1.136],
									],
                  [
		[1.39, 1.112, 0, -1.112, -1.39],
		[1.112, 1.112, 0, -1.112, -1.112],
		[-2.085, -2.085, 0, -2.085, -2.085],
		[-1.112, -1.112, 0, 1.112, 1.112],
		[-1.39, -1.112, 0, 1.112, 1.39],
									],
                  [
		[1.36, 1.088, 0, -1.088, -1.36],
		[1.088, 1.088, 0, -1.088, -1.088],
		[-2.0425, -2.0425, 0, -2.0425, -2.0425],
		[-1.088, -1.088, 0, 1.088, 1.088],
		[-1.36, -1.088, 0, 1.088, 1.36],
									],
                                    ]

if __name__ == "__main__":
    app.run(host='0.0.0.0')
    
@app.route('/')
def compute8v():
	#answers = '3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3'
	answers = [int(x) for x in str(request.args.get("answers"))[::2]]
	favorite = request.args.get("favorite")
    
	resultsPerCandidate = {
	  'Andres Manuel Lopez Obrador' : [
	    0,
      'Andrés Manuel López Obrador',
      'JUNTOS HAREMOS HISTORIA (MORENA-PT-PES)',
      'Educación',
      'x',
      'https://pbs.twimg.com/profile_images/941387100095635456/CmULmyyk_400x400.jpg',
      [0,0,0,0,0,0,0,]
      ],
    
    'Ricardo Anaya' : [
      0,
      'Ricardo Anaya',
      'POR MEXICO, AL FRENTE (PAN-PRD-MC)',
      'México y el mundo',
      'x',
      'https://pbs.twimg.com/profile_images/696899956712435712/IPsP1eSj_400x400.jpg',
      [0,0,0,0,0,0,0,]
      ],
      
    'Jose Antonio Meade' : [
      0,
      'José Antonio Meade',
      'TODOS POR MÉXICO (PRI-PVEM-PANAL)',
      'Salud y seguridad social',
      'x',
      'https://pbs.twimg.com/profile_images/979597895111294976/CAsjaezd_400x400.jpg',
      [0,0,0,0,0,0,0,]
      ],
      
    # 'Margarita Zavala' : [
    #   0,
    #   'Margarita Zavala',
    #   'INDEPENDIENTE',
    #   'Economía familiar y general',
    #   'x',
    #   'https://pbs.twimg.com/profile_images/991300977977430017/2JkiB-Lw_400x400.jpg',
    #   [0,0,0,0,0,0,0,]
    #   ],
      
    'Jaime Rodriguez' : [
      0,
      'Jaime Rodríguez "El Bronco"',
      'INDEPENDIENTE',
      'Gobernanza, corrupción e impunidad',
      'x',
      'https://pbs.twimg.com/profile_images/956363270000017408/OA0M9pWj_400x400.jpg',
      [0,0,0,0,0,0,0,]
      ]
	}
	
	# The bias, which comes from the client side, is added
	resultsPerCandidate[favorite][0] = 1
	
	print(resultsPerCandidate)

	for candidate in candidatesVectors:
		for index in range(40):
			column = answers[index]-1
			row = candidatesVectors[candidate][index]-1
			parsedCandidate = resultsPerCandidate[candidate]
			if (1 <= index+1 and index+1 <= 8):
			    parsedCandidate[0] += choicesMatrix[0][row][column]
			    parsedCandidate[6][0] += choicesMatrix[0][row][column]
			elif (9 <= index+1 and index+1 <=15):
			    parsedCandidate[0] += choicesMatrix[1][row][column]
			    parsedCandidate[6][1] += choicesMatrix[1][row][column]
			elif (16 <= index+1 and index+1 <=22):
			    parsedCandidate[0] += choicesMatrix[2][row][column]
			    parsedCandidate[6][2] += choicesMatrix[2][row][column]
			elif (23 <= index+1 and index+1 <=27):
			    parsedCandidate[0] += choicesMatrix[3][row][column]
			    parsedCandidate[6][3] += choicesMatrix[3][row][column]
			elif (26 <= index+1 and index+1 <=32):
			    parsedCandidate[0] += choicesMatrix[4][row][column]
			    parsedCandidate[6][4] += choicesMatrix[4][row][column]
			elif (33 <= index+1 and index+1 <=36):
			    parsedCandidate[0] += choicesMatrix[5][row][column]
			    parsedCandidate[6][5] += choicesMatrix[5][row][column]
			elif (35 <= index+1 and index+1 <=40):
			    parsedCandidate[0] += choicesMatrix[6][row][column]
			    parsedCandidate[6][6] += choicesMatrix[6][row][column]
    
        # Super weird formatting bug here. Even though the indentation for the next line makes
        # 0 sense, it is absolutely needed
        categoriesMap = [
            "Economía Familiar y General",
            "Seguridad",
            "Gobernanza, Corrupción e Impunidad",
            "Salud y Seguridad Social",
            "Educación",
            "México y el mundo",
            "Misceláneo"]
	
	for candidate in resultsPerCandidate:
	    index_of_max, _ = max(enumerate(resultsPerCandidate[candidate][6]), key=operator.itemgetter(1))
	    index_of_min, _ = min(enumerate(resultsPerCandidate[candidate][6]), key=operator.itemgetter(1))
	    resultsPerCandidate[candidate][3] = categoriesMap[index_of_max]
	    resultsPerCandidate[candidate][4] = categoriesMap[index_of_min]
	    del resultsPerCandidate[candidate][6]
	
	print(resultsPerCandidate)
	print('////////////////////////////////////////////')
	resultsPerCandidate = sorted(resultsPerCandidate.items(), key=operator.itemgetter(1), reverse=True)
	return jsonify({'results': resultsPerCandidate})