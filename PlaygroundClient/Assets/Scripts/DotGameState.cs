using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DotGameState : GameState
{
	public int NumGoodBalls = 50;
	public int NumBadBalls = 50;
	public int SpawnRadius = 10;
	public int Reward = 1;
	public int Penalty = -1;
	public Transform robot;
	public GameObject gBall;
	public GameObject bBall;
	
	// Use this for initialization
	void Start ()
	{
		 SpawnBalls();
	}
	
	// Update is called once per frame
	void Update () {
		
	}

	void OnTriggerEnter(Collider col)
	{
		if (col.gameObject.name.Contains(gBall.name))
		{
			Destroy(col.gameObject);
			score += Reward;
		}
		if (col.gameObject.name.Contains(bBall.name))
		{
			score += Penalty;
			Destroy(col.gameObject);
		}
	}
	
	void SpawnBalls()
	{

		for (var i = 0; i < NumGoodBalls; i++)
		{
			SpawnBall(gBall);
		}
		for (var i = 0; i < NumBadBalls; i++)
		{
			SpawnBall(bBall);
		}
	}

	void SpawnBall(GameObject ball)
	{
		var location = robot.transform.position;
		location.x += Random.Range(-SpawnRadius, SpawnRadius);
		location.y = robot.position.y + .1f;
		location.z += Random.Range(-SpawnRadius, SpawnRadius);
		Instantiate(ball, location, Quaternion.identity);
	}
}
