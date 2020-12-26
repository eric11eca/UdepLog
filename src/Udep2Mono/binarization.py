class BinaryDependencyTree:
    def __init__(self, val, left, right, key, wid=None, npos=None):
        self.val = val
        self.parent = ""
        self.left = left
        self.right = right
        self.mark = "0"
        self.id = wid
        self.npos = npos
        self.key = key
        self.isRoot = False

    def setRoot(self):
        self.isRoot = True

    def isTree(self):
        return not (type(self.left) is str and type(self.right) is str)

    def getVal(self):
        return self.val

    def getLeft(self):
        return self.left

    def getRight(self):
        return self.right


priority = ["conj-sent", "case", "cc", "mark", "nsubj", "conj-vp",
            "ccomp", "advcl", "advmod", "nmod",
            "nmod:tmod", "nmod:npmod", "nmod:poss",
            "xcomp", "aux", "aux:pass", "obj",
            "cop", "acl", "acl:relcl", "appos",
            "conj-np", "conj-adj", "det", "compound",
            "amod", "conj-vb"]
queue = {}
for i in range(len(priority)):
    queue[priority[i]] = i


class Binarizer:
    def __init__(self, parseTable=None, postag=None, words=None):
        self.postag = postag
        self.parseTable = parseTable
        self.words = words
        self.id = 0

    def process_not(self, children):
        if len(children) > 1:
            if children[0][0] == "advmod":
                if self.words[children[1][1]][0] == "not":
                    return [children[1]]
        return children

    def compose(self, head):
        children = list(filter(lambda x: x[2] == head, self.parseTable))
        children.sort(key=(lambda x: queue[x[0]]))
        # key=(lambda x: (x[2]-x[1])*20 if x[2] > x[1] else abs(x[2]-x[1])), reverse=True)
        children = self.process_not(children)
        if len(children) == 0:
            word = self.words[head][0]
            tag = self.words[head][1]
            binaryTree = BinaryDependencyTree(
                word, "N", "N", self.id, head, tag)
            self.id += 1
            return binaryTree, [binaryTree.key]
        else:
            topDep = children[0]
        self.parseTable.remove(topDep)

        left, left_rel = self.compose(topDep[1])
        right, right_rel = self.compose(topDep[2])
        dep_rel = "conj" if "conj" in topDep[0] else topDep[0]
        binaryTree = BinaryDependencyTree(dep_rel, left, right, self.id)

        binaryTree.left.parent = binaryTree
        binaryTree.right.parent = binaryTree

        left_rel.append(binaryTree.key)
        self.id += 1
        return binaryTree, left_rel + right_rel

    def binarization(self):
        self.id = 0
        self.relation = []
        root = list(filter(lambda x: x[0] == "root", self.parseTable))[0][1]
        binary_tree, relation = self.compose(root)
        binary_tree.setRoot()
        return binary_tree, relation
