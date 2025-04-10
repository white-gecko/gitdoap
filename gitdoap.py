from rdflib import Graph, URIRef, Literal, RDF, RDFS, DOAP, DCTERMS as DCT, FOAF
from rdflib.namespace import Namespace
from github import Github
from urllib.parse import urlparse

# Semantically-Interlinked Online Communities
# https://www.w3.org/submissions/sioc-spec/
SIOC = Namespace("http://rdfs.org/sioc/ns#")

# Semantically-Interlinked Online Developer Communities
SIODC = Namespace("https://siodc.example.org/#")

def doapit(repo_url: str) -> Graph | None:
    """Return a Graph with a DOAP or None, if nothing could be found or it is unsupported."""
    parsed = urlparse(repo_url)
    if parsed.hostname == "github.com":
        return githubdoap(repo_url)
    return None

def normalize_github(repo_url: str, base_url: str = "https://github.com/") -> tuple(str, str):
    """Normalize the repo_url an return it together with the repository name."""
    repo_url = repo_url.removesuffix(".git")
    repo_url = repo_url.removeprefix("https://")
    repo_url = repo_url.removeprefix("http://")
    repo_url = f"https://{repo_url}"
    repo_name = repo_url.removeprefix(base_url)
    return repo_url, repo_name

def github_doap(repo_url: str, base_url: str = "https://github.com/") -> Graph:
    """Construct a description from based on the results from the GitHub API."""
    repo_url, repo_name = normalize_github(repo_url, base_url)

    gh = Github()
    repo = gh.get_repo(repo_name)

    g = Graph()
    repo_resource = g.resource(repo_url)
    repo_resource.add(RDF.type, DOAP.Project)
    repo_resource.add(DOAP.description, Literal(repo.description))
    repo_resource.add(DOAP.developer, URIRef(repo.owner.html_url))
    repo_resource.add(DOAP.homepage, URIRef(repo.homepage))
    repo_resource.add(DOAP.repository, URIRef(repo.clone_url))
    repo_resource.add(DOAP.repository, URIRef(repo.svn_url))
    repo_resource.add(DOAP.created, Literal(repo.created_at))
    repo_resource.add(DCT.date, Literal(repo.updated_at))
    repo_resource.add(DOAP.license, URIRef(repo.license.url))
    repo_resource.add(SIODC.num_stars, Literal(repo.stargazers_count))
    repo_resource.add(SIODC.num_watchers, Literal(repo.subscribers_count))
    if repo.issues_url:
        repo_resource.add(SIODC.issue_tracker, URIRef(repo_url + "/issues"))

    developer_resource = g.resource(URIRef(repo.owner.html_url))
    # The typing is not yet cool, since doap:developer will make it a foaf:Person anyhow
    developer_resource.add(RDF.type, FOAF.Agent)
    if repo.owner.type == "Organization":
        developer_resource.add(RDF.type, FOAF.Organization)
    if repo.owner.type == "User":
        developer_resource.add(RDF.type, SIOC.User)

    license_resource = g.resource(URIRef(repo.license.url))
    license_resource.add(RDFS.label, Literal(repo.license.name))

    git_repo_resource = g.resource(URIRef(repo.git_url))
    # The typing is not yet cool, since doap:developer will make it a foaf:Person anyhow
    git_repo_resource.add(RDF.type, DOAP.GitRepository)
    git_repo_resource.add(DOAP.repository, URIRef(repo.clone_url))
    git_repo_resource.add(DOAP.repository, URIRef(repo.ssh_url))

    svn_repo_resource = g.resource(URIRef(repo.svn_url))
    # The typing is not yet cool, since doap:developer will make it a foaf:Person anyhow
    svn_repo_resource.add(RDF.type, DOAP.SVNRepository)
    svn_repo_resource.add(DOAP.repository, URIRef(repo.svn_url))

    return g
