# Zero propulsion test

Sensor read out to support the propulsion and regeneration tests for Zero.

## Development

A devcontainer is included. The pyADS used to interface with the TwinCAT PLC doesn't support MacOS.

## Deployment

To get around the network difficulties running this on the cluster, this is temporarily deployed on a Raspberry Pi. Access to that is through the VPN with ssh.

To speed up package management on that low computer environment, `uv` is used to manage the packages and run the thing.

Orchestration is done through docker compose
