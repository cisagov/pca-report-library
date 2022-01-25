ARG GIT_COMMIT=unspecified
ARG GIT_REMOTE=unspecified
ARG VERSION=unspecified

FROM python:3

ARG GIT_COMMIT
ARG GIT_REMOTE
ARG VERSION

LABEL git_commit=$GIT_COMMIT
LABEL git_remote=$GIT_REMOTE
LABEL maintainer="bryce.beuerlein@cisa.dhs.gov"
LABEL vendor="Cyber and Infrastructure Security Agency"
LABEL version=$VERSION

ARG CISA_UID=421
ENV CISA_HOME="/home/cisa"
ENV PCA_REPORT_TOOLS_SRC="/usr/src/pca-report-tools"

RUN addgroup --system --gid $CISA_UID cisa \
  && adduser --system --uid $CISA_UID --ingroup cisa cisa

# Install fonts
COPY src/pca_report_library/assets/fonts /usr/share/fonts/truetype/ncats
RUN fc-cache -fsv


RUN apt-get update && \
 apt-get install --no-install-recommends -y texlive texlive-xetex texlive-bibtex-extra

VOLUME $CISA_HOME

WORKDIR $PCA_REPORT_TOOLS_SRC
COPY . $PCA_REPORT_TOOLS_SRC

RUN pip install --no-cache-dir .
RUN chmod +x ${PCA_REPORT_TOOLS_SRC}/var/getenv
RUN ln -snf ${PCA_REPORT_TOOLS_SRC}/var/getenv /usr/local/bin

USER cisa
WORKDIR $CISA_HOME
CMD ["getenv"]
