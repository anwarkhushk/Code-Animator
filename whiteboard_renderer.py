from moviepy import ImageClip, CompositeVideoClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import json

class WhiteboardRenderer:
    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height
        self.scale = width / 1280.0
        self.variables = {} # name -> value
        self.arrays = {}    # name -> list of values
        self.pointers = {}  # name -> target info
        self.output_logs = [] # List of output strings
        self.stack = []     # List of stack frames: {"name": str, "variables": dict, "return_value": any}
        self.plots = {}     # name -> {"type": "scatter", "points": [], "line": (m, c), "residuals": bool, "axes": (xmin, xmax, ymin, ymax)}
        self.clusters = {}  # name -> {"centroids": [], "points": [], "assignments": []}
        
        # --- Color Palette (Teaching Quality) ---
        self.colors = {
            'bg': (250, 250, 250),           # Warm White #FAFAFA
            'text': (43, 43, 43),            # Soft Black #2B2B2B
            'var_fill': (232, 238, 247),     # #E8EEF7
            'var_border': (74, 111, 165),    # #4A6FA5 (Soft Blue)
            'arr_fill': (255, 255, 255),     # #FFFFFF
            'arr_border': (204, 204, 204),   # #CCCCCC
            'highlight_cell_fill': (255, 243, 176), # #FFF3B0
            'highlight_cell_border': (230, 184, 0), # #E6B800
            'highlight_var_fill': (220, 235, 255),  # #DCEBFF
            'highlight_var_border': (91, 155, 213), # #5B9BD5
            'shadow': (200, 200, 200, 100),         # Transparent gray
            'pointer': (220, 50, 50),               # Standard Red for now, refined later
            'overlay_bg': (245, 245, 245),
            'title': (43, 43, 43),
            'stack_fill': (245, 245, 255),  # Very light blue-white
            'stack_border': (150, 150, 200) # Muted blue
        }

        # --- Fonts ---
        self.font_main = None
        self.font_large = None
        self.font_small = None
        self.font_title = None

        font_candidates = ["consola.ttf", "verdana.ttf", "arial.ttf"]
        
        def load_font(name, size):
            try:
                # Apply scale to font size
                return ImageFont.truetype(name, int(size * self.scale))
            except IOError:
                return None

        for font_name in font_candidates:
            if not self.font_main:
                self.font_main = load_font(font_name, 24)
                self.font_large = load_font(font_name, 32)
                self.font_small = load_font(font_name, 18)
                self.font_title = load_font(font_name, 30)
        
        if not self.font_main:
            self.font_main = ImageFont.load_default()
            self.font_large = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
            self.font_title = ImageFont.load_default()

        # Transient state
        self.highlighted_variables = set() 
        self.highlighted_indices = {}      
        self.overlay_text = None           
        self.current_title = ""
        self.max_output_lines = 5
        self.frames_to_pop = [] # Frames to remove at the start of the next scene

    def _create_base_image(self):
        return Image.new('RGB', (self.width, self.height), self.colors['bg'])

    def _draw_rounded_rect(self, draw, xy, fill, outline, width=1, radius=12, shadow=True):
        """
        Draws a rounded rectangle with optional shadow.
        xy: [x1, y1, x2, y2]
        """
        x1, y1, x2, y2 = xy
        
        if shadow:
            # Draw shadow offset
            shadow_offset = int(4 * self.scale)
            draw.rounded_rectangle(
                [x1 + shadow_offset, y1 + shadow_offset, x2 + shadow_offset, y2 + shadow_offset],
                radius=radius,
                fill=self.colors['arr_border']
            )

        draw.rounded_rectangle(
            [x1, y1, x2, y2],
            radius=radius,
            fill=fill,
            outline=outline,
            width=width
        )

    def _draw_variables_panel(self, draw):
        """Draws variables in a sidebar on the left."""
        panel_width = int(300 * self.scale)
        start_x = int(40 * self.scale)
        start_y = int(100 * self.scale)
        
        # Panel Title
        draw.text((start_x, start_y - int(40 * self.scale)), "Variables", font=self.font_large, fill=self.colors['text'])
        
        y_offset = start_y
        
        for name, value in self.variables.items():
            # Style
            is_highlighted = name in self.highlighted_variables
            fill = self.colors['highlight_var_fill'] if is_highlighted else self.colors['var_fill']
            outline = self.colors['highlight_var_border'] if is_highlighted else self.colors['var_border']
            width = int(3 * self.scale) if is_highlighted else int(2 * self.scale)
            
            # Box dimensions
            box_h = int(60 * self.scale)
            box_w = int(220 * self.scale)
            
            self._draw_rounded_rect(draw, [start_x, y_offset, start_x + box_w, y_offset + box_h], 
                                    fill=fill, outline=outline, width=width, radius=int(10 * self.scale))
            
            # Text: "name = value"
            text_str = f"{name} = {value}"
            text_x = start_x + int(15 * self.scale)
            text_y = y_offset + int(15 * self.scale)
            
            draw.text((text_x, text_y), text_str, font=self.font_main, fill=self.colors['text'])
            
            y_offset += int(80 * self.scale) # Next variable

    def _draw_arrays_area(self, draw):
        """Draws arrays in the center area."""
        center_x = self.width // 2 + int(100 * self.scale) # Shifted right because of sidebar
        start_y = int(200 * self.scale)
        
        self.array_positions = {} # Store for pointers
        
        for name, values in self.arrays.items():
            # Array Title
            title_w = draw.textlength(name, font=self.font_large)
            draw.text((center_x - title_w//2, start_y - int(50 * self.scale)), name, font=self.font_large, fill=self.colors['text'])
            
            cell_size = int(70 * self.scale)
            spacing = int(10 * self.scale)
            total_width = len(values) * (cell_size + spacing) - spacing
            start_x = center_x - total_width // 2
            
            self.array_positions[name] = (start_x, start_y, cell_size, spacing)
            
            highlights = self.highlighted_indices.get(name, set())
            
            current_x = start_x
            for i, val in enumerate(values):
                is_highlighted = i in highlights
                fill = self.colors['highlight_cell_fill'] if is_highlighted else self.colors['arr_fill']
                outline = self.colors['highlight_cell_border'] if is_highlighted else self.colors['arr_border']
                width = int(3 * self.scale) if is_highlighted else int(2 * self.scale)
                
                # Draw Cell
                self._draw_rounded_rect(draw, 
                                      [current_x, start_y, current_x + cell_size, start_y + cell_size],
                                      fill=fill, outline=outline, width=width, radius=int(8 * self.scale))
                
                # Draw Value
                val_str = str(val)
                bbox = draw.textbbox((0,0), val_str, font=self.font_large)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
                
                draw.text((current_x + (cell_size - text_w)/2, start_y + (cell_size - text_h)/2 - int(4 * self.scale)), 
                          val_str, font=self.font_large, fill=self.colors['text'])
                
                # Draw Index
                idx_str = str(i)
                draw.text((current_x + int(5 * self.scale), start_y + cell_size + int(5 * self.scale)), idx_str, font=self.font_small, fill=(150,150,150))
                
                current_x += cell_size + spacing
                
            start_y += int(180 * self.scale) # Gap for next array

    def _draw_pointers(self, draw):
        for name, target_info in self.pointers.items():
            target = target_info.get('target')
            index = int(target_info.get('index', 0))
            
            if target in self.array_positions:
                start_x, start_y, cell_size, spacing = self.array_positions[target]
                
                # Calculate center of target cell
                cell_x = start_x + index * (cell_size + spacing)
                center_x = cell_x + cell_size // 2
                top_y = start_y
                
                # Pointer characteristics
                ptr_color = self.colors['pointer']
                arrow_y = top_y - int(10 * self.scale)
                tail_len = int(30 * self.scale)
                
                # Draw Arrow Head
                draw.polygon([
                    (center_x, arrow_y + int(10 * self.scale)), 
                    (center_x - int(8 * self.scale), arrow_y - int(8 * self.scale)), 
                    (center_x + int(8 * self.scale), arrow_y - int(8 * self.scale))
                ], fill=ptr_color)
                
                # Draw Line
                draw.line([(center_x, arrow_y - int(8 * self.scale)), (center_x, arrow_y - int(8 * self.scale) - tail_len)], fill=ptr_color, width=int(3 * self.scale))
                
                # Draw Label
                label_y = arrow_y - int(8 * self.scale) - tail_len - int(25 * self.scale)
                label_w = draw.textlength(name, font=self.font_main)
                draw.text((center_x - label_w//2, label_y), name, font=self.font_main, fill=ptr_color)

    def _draw_title_bar(self, draw):
        if self.current_title:
            w = draw.textlength(self.current_title, font=self.font_title)
            draw.text(((self.width - w)/2, int(30 * self.scale)), self.current_title, font=self.font_title, fill=self.colors['text'])

    def _draw_overlay(self, draw):
        if self.overlay_text:
            # Bottom overlay bar
            bar_height = int(80 * self.scale)
            y_start = self.height - bar_height - int(20 * self.scale)
            
            self._draw_rounded_rect(draw, 
                                  [int(100 * self.scale), y_start, self.width - int(100 * self.scale), y_start + bar_height],
                                  fill=self.colors['overlay_bg'], 
                                  outline=self.colors['arr_border'],
                                  width=1, radius=int(15 * self.scale), shadow=True)
            
            # Text
            w = draw.textlength(self.overlay_text, font=self.font_main)
            draw.text(((self.width - w)/2, y_start + int(25 * self.scale)), self.overlay_text, font=self.font_main, fill=self.colors['text'])

    def _draw_output_panel(self, draw):
        """Draws a 'Console' or 'Output' box on the bottom right."""
        if not self.output_logs:
            return
            
        panel_width = int(350 * self.scale)
        panel_height = int(150 * self.scale)
        margin = int(40 * self.scale)
        
        start_x = self.width - panel_width - margin
        start_y = self.height - panel_height - margin - int(100 * self.scale) # Above the overlay if it exists
        
        # If overlay exists, move up
        if self.overlay_text:
            start_y -= int(20 * self.scale)
        else:
            start_y = self.height - panel_height - margin
            
        # Draw Box
        self._draw_rounded_rect(draw, [start_x, start_y, start_x + panel_width, start_y + panel_height],
                                fill=(30, 30, 30), # Dark terminal color
                                outline=(100, 100, 100),
                                width=1, radius=int(10 * self.scale), shadow=True)
        
        # Title "Output"
        draw.text((start_x + int(15 * self.scale), start_y + int(10 * self.scale)), "Program Output", font=self.font_small, fill=(200, 200, 200))
        draw.line([(start_x + int(10 * self.scale), start_y + int(35 * self.scale)), (start_x + panel_width - int(10 * self.scale), start_y + int(35 * self.scale))], fill=(100, 100, 100))
        
        # Display logs (last N lines)
        logs_to_show = self.output_logs[-self.max_output_lines:]
        y_text = start_y + int(45 * self.scale)
        for log in logs_to_show:
            draw.text((start_x + int(15 * self.scale), y_text), "> " + str(log), font=self.font_small, fill=(0, 255, 0)) # Green text
            y_text += int(20 * self.scale)

    def _draw_stack_area(self, draw):
        """Draws the call stack vertically."""
        if not self.stack:
            return
            
        panel_width = int(280 * self.scale)
        margin = int(40 * self.scale)
        start_x = self.width - panel_width - margin
        
        # If output panel is present, move stack above it
        bottom_y = self.height - margin
        if self.output_logs:
            bottom_y -= int(170 * self.scale) # Shift above output panel
            
        if self.overlay_text:
            bottom_y -= int(100 * self.scale) # Shift above overlay
            
        # Draw "Call Stack" header
        draw.text((start_x, bottom_y - int(30 * self.scale) - int(100 * self.scale) * len(self.stack)), "Call Stack", font=self.font_large, fill=self.colors['text'])
        
        y_offset = bottom_y
        
        for i, frame in enumerate(self.stack):
            frame_h = int(90 * self.scale)
            y_start = y_offset - frame_h
            
            # Draw frame box
            self._draw_rounded_rect(draw, [start_x, y_start, start_x + panel_width, y_start + frame_h],
                                    fill=self.colors['stack_fill'],
                                    outline=self.colors['stack_border'],
                                    width=int(2 * self.scale), radius=int(10 * self.scale), shadow=True)
            
            # Frame Name
            name_str = f"Frame: {frame['name']}"
            draw.text((start_x + int(10 * self.scale), y_start + int(10 * self.scale)), name_str, font=self.font_main, fill=self.colors['text'])
            
            # Variables
            vars_str = ", ".join([f"{k}={v}" for k, v in frame['variables'].items()])
            if len(vars_str) > 30: vars_str = vars_str[:27] + "..."
            draw.text((start_x + int(10 * self.scale), y_start + int(45 * self.scale)), vars_str, font=self.font_small, fill=(80,80,80))
            
            # Return value if popped
            if frame.get('return_value') is not None:
                ret_str = f"Return: {frame['return_value']}"
                draw.text((start_x + int(10 * self.scale), y_start + int(65 * self.scale)), ret_str, font=self.font_small, fill=(200, 50, 50))

            y_offset -= frame_h + int(10 * self.scale) # Stack upwards

    def _draw_plots_area(self, draw):
        """Draws ML plots in the center area."""
        if not self.plots and not self.clusters:
            return

        center_x = self.width // 2 + int(100 * self.scale)
        start_y = int(150 * self.scale)
        plot_size = int(350 * self.scale)
        
        for name, data in self.plots.items():
            draw.text((center_x - plot_size//2, start_y - int(40 * self.scale)), name, font=self.font_large, fill=self.colors['text'])
            
            ax_x1 = center_x - plot_size // 2
            ax_y1 = start_y
            ax_x2 = center_x + plot_size // 2
            ax_y2 = start_y + plot_size
            
            draw.rectangle([ax_x1, ax_y1, ax_x2, ax_y2], fill=(255, 255, 255), outline=self.colors['arr_border'])
            draw.line([(ax_x1, ax_y2), (ax_x2, ax_y2)], fill=self.colors['text'], width=int(2 * self.scale))
            draw.line([(ax_x1, ax_y1), (ax_x1, ax_y2)], fill=self.colors['text'], width=int(2 * self.scale))
            
            axes = data.get('axes', (0, 10, 0, 10))
            x_min, x_max, y_min, y_max = axes
            
            def to_screen(px, py):
                nx = (px - x_min) / (x_max - x_min + 1e-6)
                ny = (py - y_min) / (y_max - y_min + 1e-6)
                sx = ax_x1 + nx * plot_size
                sy = ax_y2 - ny * plot_size
                return sx, sy

            points = data.get('points', [])
            for pt in points:
                sx, sy = to_screen(pt[0], pt[1])
                r = int(4 * self.scale)
                draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(91, 155, 213), outline=(74, 111, 165))

            line_params = data.get('line')
            if line_params:
                m, c = line_params
                lx1, ly1 = x_min, m * x_min + c
                lx2, ly2 = x_max, m * x_max + c
                lsx1, lsy1 = to_screen(lx1, ly1)
                lsx2, lsy2 = to_screen(lx2, ly2)
                draw.line([(lsx1, lsy1), (lsx2, lsy2)], fill=(200, 50, 50), width=int(3 * self.scale))
                
                if data.get('residuals'):
                    for pt in points:
                        px, py = pt
                        pred_y = m * px + c
                        sx, sy = to_screen(px, py)
                        _, syp = to_screen(px, pred_y)
                        draw.line([(sx, sy), (sx, syp)], fill=(180, 180, 180), width=1)
            
            sigmoid_params = data.get('sigmoid')
            if sigmoid_params:
                w, b = sigmoid_params
                steps = 50
                prev_p = None
                for i in range(steps + 1):
                    curr_x = x_min + (x_max - x_min) * (i / steps)
                    try:
                        import math
                        z = w * curr_x + b
                        z = max(-10, min(10, z))
                        curr_y = 1 / (1 + math.exp(-z))
                        scaled_y = y_min + curr_y * (y_max - y_min)
                        sx, sy = to_screen(curr_x, scaled_y)
                        if prev_p:
                            draw.line([prev_p, (sx, sy)], fill=(0, 150, 255), width=int(3 * self.scale))
                        prev_p = (sx, sy)
                    except Exception:
                        continue

            start_y += plot_size + int(100 * self.scale)

        for name, data in self.clusters.items():
            draw.text((center_x - plot_size//2, start_y - int(40 * self.scale)), name, font=self.font_large, fill=self.colors['text'])
            ax_x1 = center_x - plot_size // 2
            ax_y1 = start_y
            ax_x2 = center_x + plot_size // 2
            ax_y2 = start_y + plot_size
            
            draw.rectangle([ax_x1, ax_y1, ax_x2, ax_y2], fill=(255, 255, 255), outline=self.colors['arr_border'])
            draw.line([(ax_x1, ax_y2), (ax_x2, ax_y2)], fill=self.colors['text'], width=int(2 * self.scale))
            draw.line([(ax_x1, ax_y1), (ax_x1, ax_y2)], fill=self.colors['text'], width=int(2 * self.scale))
            
            axes = data.get('axes', (0, 10, 0, 10))
            x_min, x_max, y_min, y_max = axes
            
            def to_screen_clu(px, py):
                nx = (px - x_min) / (x_max - x_min + 1e-6)
                ny = (py - y_min) / (y_max - y_min + 1e-6)
                return ax_x1 + nx * plot_size, ax_y2 - ny * plot_size

            cluster_colors = [
                ((255, 100, 100), (200, 50, 50)),
                ((100, 255, 100), (50, 200, 50)),
                ((100, 100, 255), (50, 50, 200)),
                ((255, 255, 100), (200, 200, 50)),
            ]

            points = data.get('points', [])
            assignments = data.get('assignments', [])
            for i, pt in enumerate(points):
                sx, sy = to_screen_clu(pt[0], pt[1])
                c_idx = assignments[i] if i < len(assignments) else -1
                fill_col, out_col = ((200, 200, 200), (150, 150, 150))
                if 0 <= c_idx < len(cluster_colors):
                    fill_col, out_col = cluster_colors[c_idx]
                r = int(4 * self.scale)
                draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=fill_col, outline=out_col)

            centroids = data.get('centroids', [])
            for i, c in enumerate(centroids):
                sx, sy = to_screen_clu(c[0], c[1])
                _, out_col = cluster_colors[i % len(cluster_colors)]
                r = int(8 * self.scale)
                draw.ellipse([sx - r, sy - r, sx + r, sy + r], outline=out_col, width=int(3 * self.scale))
                draw.ellipse([sx - int(2 * self.scale), sy - int(2 * self.scale), sx + int(2 * self.scale), sy + int(2 * self.scale)], fill=out_col)
            
            start_y += plot_size + int(100 * self.scale)

    def render_scene(self, scene_data, duration=2):
        """
        Renders a single scene.
        """
        # Clear frames marked for popping in the PREVIOUS scene
        for frame in self.frames_to_pop:
            if frame in self.stack:
                self.stack.remove(frame)
        self.frames_to_pop = []

        actions = scene_data.get('actions', [])
        
        # Check for Scene Title (new feature)
        if 'title' in scene_data:
            self.current_title = scene_data['title']
        elif 'narration_text' in scene_data:
            # Fallback: use first few words of narration as title? Or just empty.
            # Let's keep existing title if not specified, or empty.
            pass

        # Update state
        for action in actions:
            # Robustness: if value/values is a string that looks like a list/dict, try parsing it
            for key in ['values', 'value', 'points', 'centroids', 'assignments', 'axes', 'line', 'variables', 'new_value']:
                if key in action and isinstance(action[key], str):
                    val_str = action[key].strip()
                    if (val_str.startswith('[') and val_str.endswith(']')) or \
                       (val_str.startswith('{') and val_str.endswith('}')):
                        try:
                            action[key] = json.loads(val_str)
                        except:
                            pass

            atype = action.get('type')
            if atype == 'draw_variable':
                self.variables[action['name']] = str(action['value'])
            elif atype == 'update_value':
                self.variables[action['name']] = str(action['new_value'])
            elif atype == 'draw_array':
                self.arrays[action['name']] = action['values']
            elif atype == 'update_array_value':
                name = action['name']
                idx = int(action['index'])
                val = action['new_value']
                if name in self.arrays:
                    self.arrays[name][idx] = val
            elif atype == 'draw_pointer' or atype == 'move_pointer':
                 self.pointers[action['name']] = {'target': action['target'], 'index': action['index']}
            elif atype == 'highlight_variable':
                self.highlighted_variables.add(action['name'])
            elif atype == 'highlight_index':
                arr_name = action.get('name', action.get('array_name'))
                if arr_name:
                    if arr_name not in self.highlighted_indices:
                        self.highlighted_indices[arr_name] = set()
                    self.highlighted_indices[arr_name].add(int(action['index']))
            elif atype == 'clear_highlights':
                self.highlighted_variables.clear()
                self.highlighted_indices.clear()
                self.overlay_text = None
            elif atype == 'swap_array_values':
                arr_name = action.get('name', action.get('array_name'))
                idx1 = int(action.get('index1'))
                idx2 = int(action.get('index2'))
                if arr_name in self.arrays:
                    arr = self.arrays[arr_name]
                    if 0 <= idx1 < len(arr) and 0 <= idx2 < len(arr):
                        arr[idx1], arr[idx2] = arr[idx2], arr[idx1]
            elif atype == 'show_text':
                self.overlay_text = action.get('text')
            elif atype == 'print_output':
                self.output_logs.append(str(action.get('text', '')))
            elif atype == 'push_stack_frame':
                self.stack.append({
                    'name': action.get('name', 'Anonymous'),
                    'variables': action.get('variables', {}),
                    'return_value': None
                })
            elif atype == 'pop_stack_frame':
                if self.stack:
                    # Provide return value for THIS scene's visual
                    self.stack[-1]['return_value'] = action.get('return_value')
                    # Mark for removal at the start of the NEXT scene
                    self.frames_to_pop.append(self.stack[-1])
            elif atype == 'update_frame_variable':
                if self.stack:
                    self.stack[-1]['variables'][action['name']] = str(action['value'])
            elif atype == 'draw_plot':
                self.plots[action['name']] = {
                    'type': action.get('plot_type', 'scatter'),
                    'points': action.get('points', []),
                    'axes': action.get('axes', (0, 10, 0, 10)),
                    'line': action.get('line'),
                    'sigmoid': action.get('sigmoid'),
                    'residuals': action.get('residuals', False)
                }
            elif atype == 'update_plot':
                name = action['name']
                if name in self.plots:
                    if 'line' in action: self.plots[name]['line'] = action['line']
                    if 'sigmoid' in action: self.plots[name]['sigmoid'] = action['sigmoid']
                    if 'points' in action: self.plots[name]['points'] = action['points']
                    if 'residuals' in action: self.plots[name]['residuals'] = action['residuals']
            elif atype == 'draw_clusters':
                self.clusters[action['name']] = {
                    'points': action.get('points', []),
                    'centroids': action.get('centroids', []),
                    'assignments': action.get('assignments', []),
                    'axes': action.get('axes', (0, 10, 0, 10))
                }
            elif atype == 'update_clusters':
                name = action['name']
                if name in self.clusters:
                    if 'points' in action: self.clusters[name]['points'] = action['points']
                    if 'centroids' in action: self.clusters[name]['centroids'] = action['centroids']
                    if 'assignments' in action: self.clusters[name]['assignments'] = action['assignments']
        
        # Create image
        img = self._create_base_image()
        draw = ImageDraw.Draw(img)
        
        # Draw Layers
        self._draw_title_bar(draw)
        self._draw_variables_panel(draw)
        self._draw_arrays_area(draw)
        self._draw_plots_area(draw)
        self._draw_pointers(draw)
        self._draw_stack_area(draw)
        self._draw_output_panel(draw)
        self._draw_overlay(draw)
        
        img_np = np.array(img)
        
        try:
            clip = ImageClip(img_np).with_duration(duration)
        except AttributeError:
            clip = ImageClip(img_np).set_duration(duration)
            
        return clip

    def save_temp_image(self, img, path):
         img.save(path)
