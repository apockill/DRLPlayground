﻿using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Robot : MonoBehaviour
{
	public float MaxAcceleration = 3f;
	public float AccelerationConst = 1f;
	public float RotationConst = 180f;
	
	private float _acceleration = 0.05f;
	private float _movementSpeed = 0f;
	private float _rotationSpeed = 0f;

	private Rigidbody _rb;
	

	public void Awake () {
		_rb = GetComponent<Rigidbody>();
	}

	public void Update () {
		// Move
		var movement = transform.forward * _movementSpeed * Time.deltaTime;
		_rb.MovePosition(_rb.position + movement);
		
		// Turn
		var turn = _rotationSpeed * Time.deltaTime;
		var turnRotation = Quaternion.Euler(0f, turn, 0f);
		_rb.MoveRotation(_rb.rotation * turnRotation);
	}
    
    public void ProcessCommand(int command)
    {
	    /* 0: do nothing (decelerate slowly)
	     * 1: forward
	     * 2: backward
	     * 3: turn left
	     * 4: turn right
	     */
	    
	    // Reset variables from the previous command
	    _rotationSpeed = 0;
	    
	    // Perform the command
	    if (command == 0)
		    Decelerate();
	    if (command == 1)
		    Accelerate(1);
	    if (command == 2)
		    Accelerate(-1);
	    if (command == 3)
		    TurnLeft();
	    if (command == 4)
		    TurnRight();
	}

	private void Accelerate(int direction)
	{
		// Direction is either 1 or -1
		_movementSpeed += _acceleration * AccelerationConst * direction;
	}

	private void Decelerate()
	{
		// Slow down
		if (_movementSpeed > 0){
			_movementSpeed -= Mathf.Lerp(_acceleration, MaxAcceleration, 0f);
		}
		else if (_movementSpeed < 0){
			_movementSpeed += Mathf.Lerp(_acceleration, -MaxAcceleration, 0f);
		}
		else{
			_movementSpeed = 0;
		}
	}

	private void TurnRight()
	{
		_rotationSpeed += RotationConst;
	}

	private void TurnLeft()
	{
		_rotationSpeed -= RotationConst;
	}
	
}
