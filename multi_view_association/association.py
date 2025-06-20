import os 
import numpy as np 
import pdb
import cv2
from multi_view_association.association import GridDeterminer


class Point(object):
    def __init__(self, x, y, view, is_distorted=True):
        '''
        input:
            x,y: float point location
            view: View Object
            is_distorted: True is the distorted point, else wise
        output: 
            None
        '''
        self.x = x 
        self.y = y 
        self.view = view 
        self.is_distorted = is_distorted
        self.grid = self.get_grid()
    
    def get_grid(self):
        '''
        func:
            [TODO] find the grid index from points of a view
            you should first anti_distortion according to the view distortion matrix
            and find the grid index according to the grid coordinates
        input:
            None
        output:
            the Grid object of points in a view
        '''
        pass
        # return Grid
    
    def anti_distortion(self):
        '''
        func:
            [TODO] project the points from distortion to anti_distortion images according to the view distortion matrix
        input:
            None
        output:
            the Point object. convert point from distorted <-> anti_distorted state
        '''
        if not self.is_distorted:
            return self  # 已经是反畸变点，直接返回

        # 从view对象获取相机参数
        fx = 1621.9 * (self.view.fx_ratio if hasattr(self.view, 'fx_ratio') else 1.0)
        fy = 1856.1 * (self.view.fy_ratio if hasattr(self.view, 'fy_ratio') else 1.0)
        cx, cy = 1116.3, 742.9178

        K = np.array([[fx, 0, cx],
                      [0, fy, cy],
                      [0,  0,  1]], dtype=np.float32)

        k1 = self.view.k1
        k2 = self.view.k2
        p1 = self.view.p1
        p2 = self.view.p2
        k3 = self.view.k3

        dist_coeffs = np.array([k1, k2, p1, p2, k3], dtype=np.float32)

        # 构造点的数组，注意OpenCV需要形状为(N,1,2)
        pts = np.array([[[self.x, self.y]]], dtype=np.float32)
        # 反畸变
        undistorted_pts = cv2.undistortPoints(pts, K, dist_coeffs, P=K)
        new_x, new_y = undistorted_pts[0,0,0], undistorted_pts[0,0,1]

        # 返回反畸变后的新Point对象
        return Point(new_x, new_y, self.view, is_distorted=False)
        # else:
        #     pass
        #     self.is_distorted = True
        #     return Point



class Grid(object):
    def __init__(x, y, view):
        '''
        input:
            x, y: int number of object grid index
            view: View object
        output:
            None
        '''
        self.x, self.y
        self.view = view
    
    def projection(self, view):
        '''
        func:
            [TODO] according to grid view and input view, find the projection grid on the input view
            used for association function
        input: 
            View object
        output:
            grid: Grid object of the projection grid on input view
        '''
        pass 
        return grid

class View(object):
    def __init__(self, name, p1=0, p2=0, k1=0, k2=0, k3=0,fx_ratio=0,fy_ratio=0):
        '''
        input: 
            init matrix of the view camera, used for projection
            [TODO] you could add useful grid information
        output:
            None
        '''
        self.name = name
        self.p1 = p1
        self.p2 = p2
        self.k1 = k1
        self.k2 = k2 
        self.k3 = k3  # optional, could be used for more complex distortion
        self.fx_ratio = fx_ratio
        self.fy_ratio = fy_ratio


class LabelData(object):
    def __init__(self, objects=[]):
        '''
        input:
            [(id, x, y, w, h), ...], a list store the labels data of a image sample
        output:
            None
        '''
        self.objects = []
        self.objects += objects
    
    def update(self, object):
        '''
        input:
            (id, x1, y1, x2, y2)
        output: 
            None
        '''
        self.objects.append(object)


class ImageData(object):
    def __init__(self, image_path, labels=None):
        '''
        input:
            image_path: str, the image path
            labels: LabelData object, used for inference in the system
        output:
            None
        '''
        self.image_path = image_path
        self.labels = labels
    
    def update(self, label):
        '''
        func:
            update the labels
        input:
            (id, x1, y1, x2, y2)
        output: 
            None
        '''
        self.labels.update(label)

class ViewAssociation(object):
    def __init__(self, view1, view2):
        '''
        input: 
            view1, view2: View objects
            [TODO] other necessary parameters.
        '''
        self.view1 = view1
        self.view2 = view2
    
    def grid_projection(self, Grid):
        '''
        func:
            init the parameters of view1 and view2, used for grid projection fuction.
            in which given grid object of view2, find the corresponding grid object in view1
        input:
            Grid: grid object in view2
        output:
            None, init necessary parameters
        [TODO]
        '''
        pass 

class MultiViewAssociation(object):
    def __init__(self, img_root, label_root):
        self.img_root = img_root
        self.label_root = label_root
        self.views = self.init_views()
        self.main_view = self.views[0]
        self.asso_views = self.views[1:]
        self.views_imgs = self.scan_files()
        self.views_projections = self.init_view_association()
    
    def init_views(self):
        '''
        func:
            init the view parameter used for association
            init the view name p1~p3, k1~k2
            [TODO]: init the grid-wise weight used for multi view association
        '''
        view1 = View('1', p1=0, p2=0, k1=-0.5353, k2=0.2875, k3=0.0906, fx_ratio=1.33, fy_ratio=1.33)
        view2 = View('2', p1=0, p2=0, k1=-0.5153, k2=0.2845, k3=-0.0906, fx_ratio=1.34, fy_ratio=1.34)
        view3 = View('3', p1=0, p2=0, k1=-0.5253, k2=0.2845, k3=-0.0906, fx_ratio=1.34, fy_ratio=1.34)
        view4 = View('4', p1=0, p2=0, k1=-0.5253, k2=0.2875, k3=-0.0906, fx_ratio=1.34, fy_ratio=1.34)
        views = [view1, view2, view3, view4]
        return views


    
    def init_view_association(self):
        '''
        func:
            init the view projection of view1 <-> view2, view1 <-> view3, view1 <-> view4
            used for the view projection
        input:
            None 
        output: dict()
            {
            ('1', '2'): ViewAssociation object,
            ('1', '3'): ViewAssociation object,
            ('1', '4'): ViewAssociation object,
            }
        '''
        views_projections = dict()
        MainView = self.main_view
        for View in self.asso_views:
            views_projections[f"({MainView.name},{View.name})"] = ViewAssociation(MainView, View)
        
        return views_projections

    def read_label(self, view):
        '''
        input: 
            view: str, the name of the view folder
        output:
            view data: [ImageData, ImageData, ...]
        '''
        lines = []
        with open(os.path.join(self.label_root, view, 'normal_seq.txt'), 'r') as f:
            lines += f.readlines()
        
        try:
            with open(os.path.join(self.label_root, view, 'abnormal_seq.txt'), 'r') as f:
                lines += f.readlines()
        except: 
            pass
        lines = sorted(lines)
        images = [os.path.join(self.img_root, view, x) for x in sorted(list(filter(lambda x: x.endswith('.jpg'), list(next(os.walk(os.path.join(self.img_root, view)))[2]))))]

        res = []
        for image in images:
            res.append(ImageData(image, LabelData()))
        
        for line in lines:
            line_data = list(map(int, map(float, line.strip().split(','))))
            frame_id = line_data[0] # start from 1

            if line_data[7] != 0:   # filter the ashore person
                idx = line_data[1]
                x,y,w,h = line_data[2:6]
                res[frame_id-1].update((idx, x, y, w, h))
        return res

    def scan_files(self):
        '''
        input: 
            None
        output:
            {
            view1: [ImageData, ImageData, ...]
            view2: [ImageData, ImageData, ...]
            ...
            }

        '''
        res = dict()
        for view in self.views:
            view_data = self.read_label(view.name)
            res[view.name] = view_data
        self.seq_len = len(res[view.name])
        for view in self.views:
            assert self.seq_len == len(res[view.name]) 
        return res 

    def forward(self, idx):
        '''
        func:
            the main function of multi view association
        input:
            idx: int number, frame id used for test
        output:
            [TODO]
        '''
        pdb.set_trace()
        association_data = AssociationData()
        main_image_data = self.views_imgs[self.main_view.name][idx]
        association_data.LabelData2AssociationData(main_image_data, self.main_view)
        for view in self.asso_views:
            ViewImageData = self.views_imgs[view.name][idx]
            association_data.LabelData2AssociationData(ViewImageData, view)
            association_data.associate()

        for obj in association_data.association_data[self.main_view.name]:
            print(obj[0])       #print the associate results
        
        self.visualization(association_data)    # if association error happened
    
    def visualization(self, association_data):
        '''
        func:
            [TODO] visualization the four view, including the points/grid, projection points/grid, and assocaition results
        '''
        pass
        
class AssociationData(object):
    def __init__(self):
        '''
        input:
            label_data: LabelData object
        self.association_data:
            {
            view1: [([idx], Point, Grid), ([idx], Point, Grid), ...]
            viewx: [([idx], Point, Grid), ([idx], Point, Grid), ...]
            }   
        self.vis_association_data:  # record the association process used for visualization
            {
            view1: [([idx], [img_path], [Point], [Grid]), ([idx], [img_path], [Point], [Grid]), ...]
            viewx: [([idx], [img_path], [Point], [Grid]), ([idx], [img_path], [Point], [Grid]), ...]
            }
        '''
        self.association_data = {}
        self.vis_association_data = {}
    
    def LabelData2AssociationData(self, image_data, view):
        '''
        func:
            project ImageData to the association space and update the data in association space
        input:
            image_data: ImageData object of a view
            view: View object
        output:
            update the self.association_data
        '''
        self.association_data[view.name] = []
        self.vis_association_data[view.name] = []
        for label in image_data.labels.objects:
            object_id, cx, cy = label[0], label[1], label[2]
            point = Point(cx, cy, view)
            grid = point.grid
            self.association_data[view.name].append(([object_id], point, grid))
            self.vis_association_data[view.name].append(([object_id], [image_data.image_path], [point], [grid]))
    
    def associate(self):
        '''
        func:
            associate the results of view1 and viewx, with manually set weight, 
            the weight depend on the grid and view, could be initialized on the ViewAssociation object
            could set 1 for all views and all grid in the first version for east implement
            [TODO] the short distance grid for each view should be larger, vice versa
            associate with the grid index with Hungarian algorithm, update the point location and grid
        input:
            self.association_data:
                {
                view1: [([idx], Point, Grid), ([idx], Point, Grid), ...]
                viewx: [([idx], Point, Grid), ([idx], Point, Grid), ...]
                }
        output:
            self.association_data:
                {
                view1: [([idx_view1, idx_viewx], Point', Grid'), ([idx_view1, idx_viewx], Point', Grid'), ...]
                }
            self.vis_association_data:  # record the association process used for visualization
                {
                view1: [([idx_view1, idx_viewx], [img_path_view1, img_path_viewx],  [Point_view1, Point_viewx], [Grid_view1, Grid_viewx]), ...]
                }
        [TODO]
        '''
        pass
            

img_root = r'/home/chaoqunwang/swimAD/dataset/dataset_v20250506/afternoon'
label_root = r'/home/chaoqunwang/swimAD/data_transfer/mot/dataset_v20250506/afternoon'
associator = MultiViewAssociation(img_root, label_root)
associator.forward(0)

        