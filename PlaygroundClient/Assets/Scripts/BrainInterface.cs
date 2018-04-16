using UnityEngine;
using UnityEngine.Events;
using System.Collections;
using System.IO;
using System.Net.Sockets;
using System;
using UnityEngine.SceneManagement;


// Define classes for encoding and decoding JSONs
public class StateMessage
{
    public string encodedImage; // Base64 encoded image of the screen
    public int gameScore; // The current score of the game
    public bool gameOver; // Turns True when the game should be reset, or when its been won/lost
}

public class ControlMessage
{
    public int action; // A control command in the form of an integer
    public bool resetGame; // If true, the game will be reset and the action will be disregarded
}


// Create events
public class BrainInterface : MonoBehaviour
{
    // Public
    public string Host = "localhost";
    public int Port = 1234;
    public int RenderHeight = 500;
    public int RenderWidth = 500;
    public GameState Game;

    // Communication objects
    private TcpClient _mySocket;
    private NetworkStream _theStream;

    // Events
    public ControlEvent OnInputReceived;

    public void Awake()
    {
        SetupSocket();
        Screen.SetResolution(RenderWidth, RenderHeight, false, -1);
        StartCoroutine(SendAndReceive());
    }

//    public void OnPostRender()
    IEnumerator SendAndReceive()
    {
        yield return new WaitForEndOfFrame();
        
        while (true)
        {
            // Python sends a command, which is then invoked
            var read = ReadMessage();
            Debug.Log("read" + read);
            var msg = JsonUtility.FromJson<ControlMessage>(read);

            // If the game is being reset, reset it then exit early
            if (msg.resetGame)
            {
                Game.ResetGame();
                yield return new WaitForSeconds(.5f);
                Game.ResetGame();
            }
            else
            {
                // Trigger action events here
                OnInputReceived.Invoke(msg.action);
            }
            
            // Wait for the new state
            yield return new WaitForEndOfFrame();
            
            //The new state is encoded, along with the game score and game state information
            var encodedImage = GetFrameEncoded();

            // Create the state message and send it
            var message = new StateMessage
            {
                encodedImage = encodedImage,
                gameScore = Game.Score,
                gameOver = Game.IsOver
            };
            var json = JsonUtility.ToJson(message);

            WriteMessage(json);
//            if (msg.resetGame)
//            {
//                _theStream.Close();
//                _mySocket.Close();
//                SceneManager.LoadScene(SceneManager.GetActiveScene().name);
//                yield return null;
//            }
        }
    }

    public void OnApplicationQuit()
    {
        // Send a message to the server that Unity is cutting out
        WriteMessage("QUITING!");
    }

    private void WriteMessage(string message)
    {
        var bytes = System.Text.Encoding.UTF8.GetBytes(message);
        try
        {
            _theStream.Write(bytes, 0, bytes.Length);
        }
        catch (NullReferenceException)
        {
            Debug.Log("ERROR! When sending: " + message);
            Debug.Log("NetworkStream Value: " + _theStream);
            throw;
        }

        _theStream.Flush();
    }

    private string ReadMessage()
    {
        var msg = "";
        while (msg.Length == 0 || msg[msg.Length - 1] != '}')
            msg += (char) _theStream.ReadByte();
        _theStream.Flush();
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
        Destroy(tex);
        return encodedImage;
    }


    private void SetupSocket()
    {
        try
        {
            Debug.Log("Setting up socket...");
            _mySocket = new TcpClient(Host, Port);
            _theStream = _mySocket.GetStream();
        }
        catch (Exception e)
        {
            Debug.Log("Socket error: " + e);
        }
    }
}

[Serializable]
public class ControlEvent : UnityEvent<int>
{
}

// Define the main class