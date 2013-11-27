from ponyexpress.database import db
from ponyexpress.models.package import Package
from ponyexpress.models.node import Node


def process_node_info(request_json):
    node = Node.query.filter_by(name=request_json['node']).first()

    if not node:
        # Add node
        node = Node(request_json['node'])
        db.session.add(node)

        #add the packages
        if request_json['packages']:
            for package in request_json['packages']:
                if 'sha256' in package.keys():
                    # Package sha must be uniqe, so fetch the first object
                    p = Package.query.filter_by(sha=package['sha256']).first()
                    if p:
                        node.packages.append(p)
                    else:
                        new_package = Package(package['sha256'], package['name'], package['version'])

                        # Set extended attributes as well
                        new_package.uri = package['uri']
                        new_package.architecture = package['architecture']
                        new_package.provider = package['provider']
                        new_package.summary = package['summary']

                        node.packages.append(new_package)

                        db.session.add(new_package)
        db.session.commit()
    else:
        #prepare sha dict
        pp = {}

        for p in request_json['packages']:
            if 'sha256' in p.keys():
                sha = p['sha256']
                pp[sha] = p

        # Verify package version
        for package in node.packages:
            if package.sha not in pp.keys():
                # New package version
                new_package = Package(pp['sha256'], pp['name'], pp['version'])

                # Set extended attributes as well
                new_package.uri = pp['uri']
                new_package.architecture = pp['architecture']
                new_package.provider = pp['provider']
                new_package.summary = pp['summary']

                #replace the old package
                package = new_package
                db.session.add(new_package)
        db.session.commit()


