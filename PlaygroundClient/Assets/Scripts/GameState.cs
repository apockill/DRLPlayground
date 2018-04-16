
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
