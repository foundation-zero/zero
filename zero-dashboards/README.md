# Zero Dashboards
Collections of Grafana dashboards for Zero.

## Releasing
Take care that the version in chart.yaml is used to push the chart to the Helm repository. It will override existing charts with the same name and version. Example:
 - Starting set of new features, bump the version in chart.yaml for example: 0.0.1
 - Make the changes, which can be multiple PR's, each merge 0.0.1 gets overridden.
 - Set of features is done all changes are  merged
 - Create a new PR and bump the version in chart.yaml for example: 0.0.2
