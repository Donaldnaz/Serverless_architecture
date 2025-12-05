# AWS API Gateway + Lambda Integration

This project demonstrates how to build and monitor a basic RESTful API using AWS API Gateway and AWS Lambda, including:

- Creating a mock API response
- Replacing mock integration with dynamic Lambda response
- Testing via browser and API Gateway console
- Observing execution in real-time using CloudWatch Live Tail

## Architecture

<img width="900" height="307" alt="image" src="https://github.com/user-attachments/assets/81a67159-099b-4160-afb0-158caae102e0" />


## Implementation

1. **Created an API Gateway REST API**
   - Configured a new resource and method (`GET`)
   - Integrated with a **Mock backend** to return a static JSON payload

2. **Deployed the Mock API**
   - Used the API Gateway console to create a **Stage**
   - Accessed and tested the mock response in a **web browser**

3. **Replaced Mock Integration with Lambda**
   - Created an AWS Lambda function using Node.js
   - Connected the Lambda function to the API Gateway method as the new integration
   - Deployed the updated API and validated **dynamic JSON responses**

4. **Monitored API execution using CloudWatch Live Tail**
   - Enabled **execution logging** in API Gateway stage settings
   - Used **CloudWatch Logs Insights** and **Live Tail** to observe requests, responses, and errors in real time

## Lambda Function (Node.js)

```javascript
var messages = [
    "Drilling down into data!",
    "Full stream ahead – upstream, midstream, downstream!",
    "Exploring new energy horizons!",
    "Pumping up innovation!",
    "Striking digital oil!",
    "Refining the future!",
    "On a seismic shift of success!",
    "Fueling the cloud transformation!",
    "Wells of opportunity ahead!",
    "Gushing with insights!"
];

export const handler = async (event, context) => {
    let message = messages[Math.floor(Math.random() * messages.length)];
    const response = {
        statusCode: 200,
        body: JSON.stringify({ message }),
    };
    return response;
};
````

## Testing the API

After deployment, test your API endpoint by:

* Navigating to the API Gateway **Invoke URL** in a browser
* Using tools like **Postman** or `curl`:

  ```bash
  curl https://<api-id>.execute-api.<region>.amazonaws.com/prod/your-endpoint
  ```

## Observability

### Enable CloudWatch Logs for API Gateway:

1. Go to API Gateway → Stages → Logs/Tracing
2. Enable:

   * **Access logging**
   * **Execution logging**

### Use CloudWatch Live Tail

* Navigate to **CloudWatch Logs → Log groups**
* Open the log group for your API or Lambda
* Select **Live Tail** to monitor events in real time

## Author
Anasieze Ikenna - Cloud Engineer


