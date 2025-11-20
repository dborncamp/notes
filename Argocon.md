# ArgoCon 2025

Argo COn in Atlanta, GA 11/10/2025.

Things to look into:

- argo proj labs, specifically for FIPS and mono repo help
- oci support
- GitOps Promoter
- Dex for Authentication and Access Control
- `ApplicationSets` for Argo
- DAG based workflows

Arho only manages kubernetes side of deployments.
Use Kargo for promotion.
It can watch other kinds of resources (like S3 buckets, policies, etc) that are deployed with other things (like Terraform) to know if it should be deployed.
Kargo can create a PR to do the promotion.
Go to hte Akuity booth for a book on Argo


## Rollups ans Canary deployments

Intuit scales to 116k deployments/month.
Plugins are a standalone process that runs a rpc server that can make the files needed for configuring the rollouts.
Step plugins can be used to do many things, the most common one now is to route traffic in a specific way.
Canary deployments are designed to say if something should be deployed and give an idea if something will be a problems.

Configure a rollout in a controller.
This takes a rollout type of `Rollout`.
THe Rollout has steps that you define using go.
They have run, terminate, and abort steps that need to be implemented with business logic to determine pass or fail.
Each of these steps have contexts that have their configs and outputs.
You build a binary that has those steps, and the rpc server will hit hte right operation and execute the code that you define to run.
The status of the rollout k8s object will have information that will be added into the next job, this can give information like the job id.
That is a all managed by phases, an error result will be retried indefinetly and aborted will be rolled back.
THe run method must be idempodent as it will be executed multiple times.

Be careful of...

- This is using GRPC so it is a blocking call.
- Watch the size of the state, it will make the CRD grow a lot

## Full Stack ephemeral environments using ephie

No opensource, only at seat geek now.
You need to know what versions you are depending on and ensure that what you are testing with is in a good state.
How do you manage the staging environment especially when there are more than one team and resolve the contention?
Review apps could help but synching things are problematic.
It is better to be at least semi-isolated or fully isolated.
And it needs to be ephemeral, which means that all of the dependencies need to be as well.
Use Kustomize overlays to handle isolation.
Brokers need to be isolated and everything needs to be configured to use the new instance.

Their first attempt was using a parent helm chart which was hard to test and became very fragile.
App of apps was confusing and challenging as well.
They created an operator that defines their environment that made it more extensible based on Reddit's Achillies SDK
This allowed them to create an extensible environment creator that could use special CRDs to make the environment as needed.
It also allowed them to restrict how things get deployed.
SeatGeek made a CLI called `lets-go` to handle all of this.

We could look into this as a way to test the whole system.

## How to manage releases - Panel talk

We need automation to get things promoting correctly.
Argo is not a promotions tool, it is a way to run a manifest.
Consider policy first ie production requires this, staging requires something else, that will make the business logic easier, also consider SLOs here.
Simplify as much as possible and make it easy to build, gitops promoter is a good example if this.
To change culture, you need to start with champions to get around the group think level.
Start a learning standpoint and give the champion something they can be proud of and demo, that will help them change the culture.
If using Argo, `autosync` should be enabled to make sure that git matches deployments.

With AI, your Dora metrics look great because the failure rate stays the same but they are producing more code.
Because of this more testing is needed otherwise more bugs will make it through to users.
AI can also help with this area, but it is lagging behind, there are some paid options to help.
More resources will be needed to support this so reliability matters.

Stop hacking together custom pieces, longer term that will be hard to maintain and will lead to pain.
Just pick a tool, none are perfect but getting something that is maintained is better than nothing and stop hacking.
For deployments a Declarative format is better.

## Managing volumes case study using argo

This was a hard talk to follow, basically they are using Argo to deploy everything in their clusters.
Digital ocean published a blog post about it.

Digital Ocean offers Space Object Storage which is an s3 solution.
Digital Ocean has Argo managing both data and control plane of their instance for about 20 clusters.
Argo is able to allow them to observe and be authoritative of their clusters that are rancher based but using the applicationSet and the idea of being declarative.
Ansible is used for managing the custer resources but it is applied via Argo?
Their solution is called Centralize.
Their goal is to "scale with simplicity".
ArgoCD project manages cluster level resources.
They use stork8s to manage their rancher cluster

## Air Gapped deployments (Not part of argocon)

Testing is the most important thing you can do.
Come up with a minimum inventory of everything and start installing from there.
This was a talk about how to build customers that require air-gapped implementations, they are still struggling with it.
Figure out how we want to do secret rotation.

## Scaling applications in Argo gatekeepers to enablers

Kaltura was using the app of apps (one app manages the others) pattern but it didn't scale the way they wanted.
AoA creates dependencies and coupling that is hard to debug, creates a single point of failure which does not scale.
Application sets are a scalable controller that can have multiple inputs.
It has service discovery built in and has many useful generators.
Multiple generators can be matrixed together gpt allow for multi cluster and region deployments.
Use labels for grouping and for clusters.

## GitOps for AI

JFrog Fly is a way to search Artifactory using AI.
Root Agentically repairs vulnerabilities in images.
JFrog estimates that it takes 14 to 75 hours to fully implement a CVE fix to production.
Argo workflows enable scaling the testing of all of the found AI resources.
Uses Karpenter for research engines.
Use OpenTelemetry for getting the metrics and telemetry from the service.
Scaling limitations, context, and approval gates are a problem.

## Autonomus cars

GNC is using Argo to scale their testing and test models quickly, Agile allows it to scale while being agile.
It uses batch jobs to check things like image distortion, lidar motion, etc. Basically anything that they have in a service.
