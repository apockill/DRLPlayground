using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GameState : MonoBehaviour
{
	[HideInInspector]
	public int Score;

	public bool IsOver;

	public virtual void ResetGame()
	{
	}
}
