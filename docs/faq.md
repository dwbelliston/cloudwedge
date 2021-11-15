---
icon: question
label: FAQ
---
# Frequently Asked Questions

## Should I use CloudWedge?

Here are a few questions to get a feel for what you should do.

```mermaid
flowchart TD
    00(Is CloudWedge a fit for me?);
    A(Does your organization need a monitoring solution?);
    B(Is your organization deploying a solution and can you wait for it?);
    C(Do you need fine grain access to monitoring controls?);
    D(Are you okay deploying a third party solution or shipping your data to them?);
    E(Are you against using CloudWatch?);
    F(Are you against using tags to identify what you want monitored?);
    aXXX[Just stay with what you have.]:::red;
    bXXX[Use what is coming.]:::red;
    cXXX[Use a more robust tool, like New Relic or Datadog.]:::red;
    dXXX[Lots of tools out there you can send data to.]:::red;
    eXXX[CloudWedge is a framework for using CloudWatch.]:::red;
    fXXX[Tags are a 1st class citizen in CloudWedge.]:::red;
    YYY[This could work. Deploy the Wedge!]:::green;
    00--> A;
    A -- Yes ---> aXXX;
    A -- No ----> B;
    B -- Yes ---> bXXX;
    B -- No ----> C;
    C -- Yes --> cXXX;
    C -- No ----> D;
    D -- Yes --> dXXX;
    D -- No ----> E;
    E -- Yes --> eXXX;
    E -- No ----> F;
    F -- Yes --> fXXX;
    F -- No ----> YYY;
    classDef red fill:#EF4444,color:#fff;
    classDef green fill:#10B981,color:#fff;
    classDef question fill:#818CF8,color:#fff;
```

---

## What does CloudWedge cost?

We havent found a way to charge yet. So.. I guess its free. :money_with_wings:
The only cost to you will be your AWS bill to have CloudWatch alarms and dashboards.

---

## Can you help me set it up?

For sure. Send us a message in the chat bubble below or an email at help@cloudwedge.io and we will be happy to help.