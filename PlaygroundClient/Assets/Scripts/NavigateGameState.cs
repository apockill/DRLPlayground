using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class NavigateGameState : GameState {
	public int Reward = 1;
	public int CollisionPenalty = -1;
	public Transform Robot;

	private List<Collision> _currentCollisions = new List<Collision>();
	
	// Use this for initialization
	void Start ()
	{
	}
	
	// Update is called once per frame
	void Update () {
		
	}

	void OnCollisionEnter(Collision col)
	{
		_currentCollisions.Add(col);
		Debug.Log("Collision" + col.gameObject.name);
		if (IsBadCollision(col))
		{
			Debug.Log("Bad collision!");
			score += CollisionPenalty;
		}
			 
		
	}

	void OnCollisionExit(Collision col)
	{
		_currentCollisions.Remove(col);
		Debug.Log("Collision left" + col.gameObject.name);
			 
	}


	bool IsBadCollision(Collision col)
	{
		// Returns true if the collision is NOT on the bottom side of the robot
		var fromBottom = false;
		if(col.contacts.Length > 0)
		{
			ContactPoint contact = col.contacts[0];
			if(Vector3.Dot(contact.normal, Vector3.up) > 0.5)
			{
				fromBottom = true;
			}
		}

		return !fromBottom;
	}
}
