using UnityEngine;
using UnityEngine.Events;
using System.Collections;
using System.IO;
using System.Net.Sockets;
using System;


// Define classes for encoding and decoding JSONs
public class StateMessage
{
    public string encodedImage;  // Base64 encoded image of the screen
    public int gameScore;  // The current score of the game
}

public class ControlMessage
{
    public int action;  // A control command in the form of an integer
}


// Create events
[Serializable]
public class ControlEvent : UnityEvent <int> { }

// Define the main class
public class BrainInterface : MonoBehaviour {

    // Public
    public string Host = "localhost";
    public int Port = 1234;
    public int Timeout = 2000;
    public GameState gameState;
    
    // Communication objects
    private TcpClient _mySocket;
    private NetworkStream _theStream;
    private StreamWriter _theWriter;
    private StreamReader _theReader;

    // Events
    public ControlEvent OnInputReceived;

    public void Start()
    {
        SetupSocket();
    }

    public void OnPostRender()
    {
 
        var encodedImage = GetFrameEncoded();

        // Create the state message and send it
        var message = new StateMessage();
        message.encodedImage = encodedImage;
        message.gameScore = gameState.score;
        var json = JsonUtility.ToJson(message);
        WriteMessage(json);

        // Python does machine learning work here

        var read = ReadMessage();
        var msg = JsonUtility.FromJson<ControlMessage>(read);
        
        // Trigger action events here
        OnInputReceived.Invoke(msg.action);

    }

    public void OnApplicationQuit()
    {
        // Send a message to the server that Unity is cutting out
        WriteMessage("QUITING!");
    }
    private void WriteMessage(string message)
    {

        var k = (message.Length) / 1024;
        var j = (message.Length) % 1024;

        var i = 0;
        for (; i < k; i++)
        {
            var temp = message.Substring(i * 1024, 1024);
            _theWriter.Write(temp);
            _theWriter.Flush();
        }
        var temp2 = message.Substring(i * 1024, j);
        _theWriter.Write(temp2);
        _theWriter.Flush();
    }

    private string ReadMessage()
    {
        var msg = "";
        while (msg.Length == 0 || msg[msg.Length - 1] != '}')
            msg += (char)_theStream.ReadByte();

        return msg;
    }

    private string GetFrameEncoded()
    {
        // Return the current game screen encoded in a base64 string
        var width = Screen.width;
        var height = Screen.height;

        var tex = new Texture2D(width, height, TextureFormat.RGB24, false);
        tex.ReadPixels(new Rect(0, 0, width, height), 0, 0);
        tex.Apply();

        var bytes = tex.EncodeToPNG();
        var encodedImage = Convert.ToBase64String(bytes);

        return encodedImage;
    }


    private void SetupSocket()
    {
        try
        {
            _mySocket = new TcpClient(Host, Port);

            _theStream = _mySocket.GetStream();
            _theStream.ReadTimeout = Timeout;
            _theWriter = new StreamWriter(_theStream);
            _theReader = new StreamReader(_theStream);
        }
        catch (Exception e)
        {
            Debug.Log("Socket error: " + e);
        }
    }
}
