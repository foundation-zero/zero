# Custom Grafana dockerfile from http://github.com/grafana/grafana/blob/main/packaging/docker/custom/Dockerfile
# Documented here: https://grafana.com/docs/grafana/latest/setup-grafana/configure-docker/
ARG GRAFANA_VERSION="12.3.0"

FROM grafana/grafana:${GRAFANA_VERSION}

ARG GF_GID="0"

ENV GF_PATHS_PLUGINS="/var/lib/grafana-plugins"
ENV GF_PLUGIN_RENDERING_CHROME_BIN="/usr/bin/chrome"

USER root

RUN mkdir -p "$GF_PATHS_PLUGINS" && \
    chown -R grafana:${GF_GID} "$GF_PATHS_PLUGINS"

USER grafana

ARG GF_INSTALL_PLUGINS="grafana-polystat-panel,snuids-trafficlights-panel,https://github.com/GreptimeTeam/greptimedb-grafana-datasource/releases/download/v2.1.6/info8fcc-greptimedb-datasource.zip;greptimedb-datasource"

RUN if [ ! -z "${GF_INSTALL_PLUGINS}" ]; then \
      OLDIFS=$IFS; \
      IFS=','; \
      set -e ; \
      for plugin in ${GF_INSTALL_PLUGINS}; do \
        IFS=$OLDIFS; \
        if expr match "$plugin" '.*\;.*'; then \
          pluginUrl=$(echo "$plugin" | cut -d';' -f 1); \
          pluginInstallFolder=$(echo "$plugin" | cut -d';' -f 2); \
          grafana-cli --pluginUrl ${pluginUrl} --pluginsDir "${GF_PATHS_PLUGINS}" plugins install "${pluginInstallFolder}"; \
        else \
          grafana-cli --pluginsDir "${GF_PATHS_PLUGINS}" plugins install ${plugin}; \
        fi \
      done \
    fi

COPY ./dashboard-provider.yaml /etc/grafana/provisioning/dashboards/dashboard-embedded-provider.yaml
COPY ./dashboards /embedded-dashboards
COPY ./extra /usr/share/grafana/public/extra
