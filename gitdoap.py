from rdflib import Graph, URIRef, Literal, RDF, RDFS, DOAP, DCTERMS as DCT, FOAF
from rdflib.namespace import Namespace
from github import Github

# Semantically-Interlinked Online Communities
# https://www.w3.org/submissions/sioc-spec/
SIOC = Namespace("http://rdfs.org/sioc/ns#")

# Semantically-Interlinked Online Developer Communities
SIODC = Namespace("https://siodc.example.org/#")

base_url = "https://github.com/"
repo_url = "https://github.com/PyGithub/PyGithub"
repo_name = repo_url[len(base_url):]

gh = Github()
repo = gh.get_repo(repo_name)

g = Graph()
repo_resource = g.resource(repo_url)
repo_resource.add(RDF.type, DOAP.Project)
repo_resource.add(DOAP.description, Literal(repo.description))
repo_resource.add(DOAP.developer, URIRef(repo.owner.html_url))
repo_resource.add(DOAP.homepage, URIRef(repo.homepage))
repo_resource.add(DOAP.repository, URIRef(repo.git_url))
repo_resource.add(DOAP.repository, URIRef(repo.ssh_url))
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

print(g.serialize(format="text/turtle"))
# repo_resource.add(DOAP.created, Literal(repo.updated_at))
