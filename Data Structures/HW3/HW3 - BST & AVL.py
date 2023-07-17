NO_ITEM = -1
OK = 0
import random
import sys
sys.setrecursionlimit(10**6)

class Node:
    """
    BST Node
    """

    def __init__(self, key, value=None, left=None, right=None):
        """
        Constructor for BST Node
        :param key: int
        :param value: anything
        :param left: Left son - Node or None
        :param right: Right son - Node or None
        """
        self.key = key
        self.value = value
        self.left = left
        self.right = right

    def __repr__(self):
        return 'Node: key,value=(' + str(self.key) + ',' + str(self.value) + ')'


class BST:
    """
    BST Data Structure
    """

    def __init__(self, root=None):
        """
        Constructor for BST
        :param root: root of another BST
        """
        self.root = root

    def __repr__(self):
        """
        :return: a string represent the tree
        """
        s = '--------------------------------------'
        next = True
        level_arr = []
        cur_arr = [self.root]
        while next:
            next_arr = []
            for node in cur_arr:
                if node is not None:
                    next_arr.append(node.left)
                    next_arr.append(node.right)
                else:
                    next_arr.append(None)
                    next_arr.append(None)
            level_arr.append(cur_arr)
            for tmp in next_arr:
                if tmp is not None:
                    next = True
                    break
                else:
                    next = False
            cur_arr = next_arr
        d_arr = []
        d = 0
        for i in range(len(level_arr)):
            d_arr.append(d)
            d = 2 * d + 1
        d_arr.reverse()
        for i in range(len(level_arr)):
            s += '\n' + self.__level_repr(level_arr[i], d_arr[i])
        return s

    def __level_repr(self, arr, d):
        """
        helper for repr
        """
        s = ' ' * d
        for node in arr:
            if node is None:
                s = s + '!'
            else:
                s = s + str(node.key)
            s = s + ' ' * (2 * d + 1)
        return s

    def insert(self, key, value):
        """
        Inserts a new (key,value) pair to the BST.
        In case key already exists in the BST update the node's value
        :param key: int
        :returns None
        """
        node = self.find(key)
        if node:
            node.value = value
            return
        new_node = Node(key, value)
        cur = self.root
        if cur is None:
            self.root = new_node
            return
        while cur is not None:
            if cur.key > key:
                if cur.left is None:
                    cur.left = new_node
                    return
                else:
                    cur = cur.left
            else:
                if cur.right is None:
                    cur.right = new_node
                    return
                else:
                    cur = cur.right

    def delete(self, key):
        """
        Remove the node associated with key from the BST.
        If key not in BST don't do anything.
        :param key: int
        :return: OK if deleted successfully or NO_ITEM if key not in the BST
        """
        node = self.find(key)
        if node is None:
            return NO_ITEM
        if node.left is None or node.right is None:
            node_to_delete = node
        else:
            node_to_delete = self.find_minimum(node.right)
        parent = self.find_parent(node_to_delete.key)

        if node_to_delete.left is not None:
            node_child = node_to_delete.left
        else:
            node_child = node_to_delete.right
        if parent is None:
            self.root = node_child
        else:
            if parent.left == node_to_delete:
                parent.left = node_child
            else:
                parent.right = node_child
        if node is not node_to_delete:
            node.key = node_to_delete.key
            node.value = node_to_delete.value
        return OK

    def find_parent(self, key):
        """
        If key is in the BST find the parent Node associated with key
        otherwise return None
        :param key: int
        :return: parent Node if key is in BST or None o.w.
        """
        cur = self.root
        parent = None
        while cur is not None:
            if key > cur.key:
                parent = cur
                cur = cur.right
            elif key < cur.key:
                parent = cur
                cur = cur.left
            else:
                break
        return parent

    def find_minimum(self, node):
        """
        finds the node with the minimum key in the left subtree of a node
        :param node: Node
        :return: the minimum node or the node itself if there is no left subtree
        """
        cur = node
        while cur.left is not None:
            cur = cur.left
        return cur

    def find(self, key):
        """
        If key is in the BST find the Node associated with key
        otherwise return None
        :param key: int
        :return: Node if key is in BST or None o.w.
        """
        cur = self.root
        while cur is not None:
            if key > cur.key:
                cur = cur.right
            elif key < cur.key:
                cur = cur.left
            else:
                return cur
        return cur

    def inorder_traversal(self):
        """
        :return: an array (Python list) of keys sorted according to the inorder traversal of self
        """
        if self.root is None:
            return []
        array = BST(self.root.left).inorder_traversal()
        array.append(self.root.key)
        array += BST(self.root.right).inorder_traversal()

        return array

    def preorder_traversal(self):
        """
        :return: an array (Python list) of keys sorted according to the preorder traversal of self
        """
        if self.root is None:
            return []
        array = [self.root.key]
        array += BST(self.root.left).preorder_traversal()
        array += BST(self.root.right).preorder_traversal()
        return array

    def postorder_traversal(self):
        """
        :return: an array (Python list) of keys sorted according to the postorder traversal of self
        """
        if self.root is None:
            return []
        array = BST(self.root.left).postorder_traversal()
        array += BST(self.root.right).postorder_traversal()
        array.append(self.root.key)
        return array

    @staticmethod
    def create_BST_from_sorted_arr(arr):
        """
        Creates a balanced BST from a sorted array of keys according to the algorithm from class.
        The values of each key should be None.
        :param arr: sorted array as Python list
        :return: an object of type BST representing the balanced BST
        """
        if len(arr) == 0:
            return BST()
        if len(arr) == 1:
            return BST(Node(arr[0]))
        root_id = len(arr) // 2
        root = Node(arr[root_id])
        root.left = BST.create_BST_from_sorted_arr(arr[:root_id]).root
        root.right = BST.create_BST_from_sorted_arr(arr[root_id + 1:]).root
        return BST(root)


# -------------------------------------------------------------------------------------------------------------------- #


class AVLNode(Node):
    """
    Node of AVL
    """

    def __init__(self, key, value=None, left=None, right=None):
        """
        Constructor for AVL Node
        :param key: int
        :param value: anything
        :param left: Left son - Node or None
        :param right: Right son - Node or None
        """
        super(AVLNode, self).__init__(key, value, left, right)
        self.height = 0

    def __repr__(self):
        return super(AVLNode, self).__repr__() + ',' + 'height=' + str(self.height)

    def get_balance(self):
        """
        :return: The balance of the tree rooted at self: self.left.height-self.right.height
        """
        h_left, h_right = -1, -1
        if self.left:
            h_left = self.left.height
        if self.right:
            h_right = self.right.height
        return h_left - h_right


class AVL(BST):
    """
    AVL Data Structure
    """

    def __init__(self, root=None):
        """
        Constructor for a new AVL
        :param root: root of another AVL
        """
        super(AVL, self).__init__(root)

    def insert(self, key, value):
        """
        Inserts a new (key,value) pair to the BST.
        In case key already exists in the BST update the node's value
        :param value:
        :param key: int
        :return: None
        """
        node = self.find(key)
        if node:
            node.value = value
            return None
        node_inserted = self.insert_node(key, value)
        parent = self.find_parent(node_inserted.key)
        while parent is not None:
            self.updateHeight(parent)
            if abs(parent.get_balance()) > 1:
                self.reBalance(parent)
            parent = self.find_parent(parent.key)


    def leftRotation(self, node):
        """
        Do a left rotation for a given node and updates the height accordingly
        :param node: Node
        """
        node.left = AVLNode(node.key, node.value, node.left, node.right.left)
        self.updateHeight(node.left)
        node.key = node.right.key
        node.value = node.right.value
        node.right = node.right.right
        self.updateHeight(node)

    def rightRotation(self, node):
        """
        Do a right rotation for a given node and updates the height accordingly
        :param node: Node
        """
        node.right = AVLNode(node.key, node.value, node.left.right, node.right)
        self.updateHeight(node.right)
        node.key = node.left.key
        node.value = node.left.value
        node.left = node.left.left
        self.updateHeight(node)

    def reBalance(self, node):
        """
        Rebalance the Avl by choosing the right strategy for re-balancing
        :param node: Node
        """
        h_left, h_right = -1, -1
        if node.left:
            h_left = node.left.height
        if node.right:
            h_right = node.right.height

        if h_left > h_right:
            child_node = node.left
            h_left, h_right = -1, -1
            if child_node.left:
                h_left = child_node.left.height
            if child_node.right:
                h_right = child_node.right.height
            if h_left < h_right:
                self.leftRotation(child_node)
            return self.rightRotation(node)
        else:
            child_node = node.right
            h_left, h_right = -1, -1
            if child_node.left:
                h_left = child_node.left.height
            if child_node.right:
                h_right = child_node.right.height
            if h_left > h_right:
                self.rightRotation(child_node)
            return self.leftRotation(node)

    def updateHeight(self, node):
        """
        update the given node height
        :param node: Node
        """
        if node is None:
            return
        h_left, h_right = -1, -1
        if node.left:
            h_left = node.left.height
        if node.right:
            h_right = node.right.height
        node.height = max(h_left,  h_right) + 1

    def insert_node(self, key, value):
        """
        Inserts a new (key,value) pair to the AVL.
        :param value: anything
        :param key: int
        :return AVLNode that was inserted
        """
        cur = self.root
        if cur is None:
            self.root = AVLNode(key, value)
            return AVLNode(key, value)
        while cur is not None:
            if cur.key > key:
                if cur.left is None:
                    cur.left = AVLNode(key, value)
                    return cur.left
                else:
                    cur = cur.left
            else:
                if cur.right is None:
                    cur.right = AVLNode(key, value)
                    return cur.right
                else:
                    cur = cur.right

    def delete(self, key):
        """
        Remove the node associated with key from the AVL.
        If key not in BST don't do anything.
        :param key: int
        :return: OK if deleted successfully or NO_ITEM if key not in the BST
        """
        node = self.find(key)
        if node is None:
            return NO_ITEM
        deleted_node_parent = self.delete_node(node)
        while deleted_node_parent is not None:
            self.updateHeight(deleted_node_parent)
            if abs(deleted_node_parent.get_balance()) > 1:
                self.reBalance(deleted_node_parent)
            deleted_node_parent = self.find_parent(deleted_node_parent.key)
        return OK

    def delete_node(self, node):
        """
        Remove the given node from the AVL.
        :param key: AVLNode
        :return: The parent AVLNode of the deleted Node
        """
        if node.left is None or node.right is None:
            node_to_delete = node
        else:
            if node.right.left is None:
                node_to_delete = node.right
            else:
                node_to_delete = self.find_minimum(node.right)
        parent = self.find_parent(node_to_delete.key)

        if node_to_delete.left is not None:
            node_child = node_to_delete.left
        else:
            node_child = node_to_delete.right
        if parent is None:
            self.root = node_child
        else:
            if parent.left == node_to_delete:
                parent.left = node_child
            else:
                parent.right = node_child
        if node is not node_to_delete:
            node.key = node_to_delete.key
            node.value = node_to_delete.value
        return parent

