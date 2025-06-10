#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cstdint>
#include <stdexcept>
#include <tuple>
#include <cstring>
#include <cmath>

class CIFF {
public:
    std::string magic;
    int64_t header_size = 0;
    int64_t content_size = 0;
    int64_t width = 0;
    int64_t height = 0;
    std::string caption;
    std::vector<std::string> tags;
    std::vector<std::tuple<uint8_t, uint8_t, uint8_t>> pixels;
    bool is_valid = true;

    static CIFF parse(const std::string& path) {
        CIFF ciff;
        std::ifstream file(path, std::ios::binary);
        if (!file) {
            ciff.is_valid = false;
            return ciff;
        }

        try {
            // Read magic
            char magic_buf[4];
            file.read(magic_buf, 4);
            if (file.gcount() != 4) throw std::runtime_error("Invalid magic size");
            ciff.magic = std::string(magic_buf, 4);
            if (ciff.magic != "CIFF") throw std::runtime_error("Magic mismatch");

            // Read header size
            ciff.header_size = read_int64(file);
            if (ciff.header_size < 38) throw std::runtime_error("Invalid header size");

            // Read content size
            ciff.content_size = read_int64(file);
            if (ciff.content_size < 0) throw std::runtime_error("Invalid content size");

            // Read width and height
            ciff.width = read_int64(file);
            ciff.height = read_int64(file);
            if (ciff.width < 0 || ciff.height < 0) throw std::runtime_error("Invalid dimensions");
            if (ciff.width / 2 > pow(2, 63) - 1 || ciff.height / 2 > pow(2, 63) - 1) throw std::runtime_error("Dimensions too large");
            // Validate content size
            if (ciff.content_size != ciff.width * ciff.height * 3)
                throw std::runtime_error("Content size mismatch");

            // Read caption
            char ch;
            while (file.get(ch)) {
                if (ch == '\n') break;
                ciff.caption += ch;
            }
            if (file.eof()) throw std::runtime_error("Unexpected EOF in caption");

            // Read tags
            int64_t bytes_read = 36 + ciff.caption.size() + 1;
            std::string tag;
            while (bytes_read < ciff.header_size) {
                if (!file.get(ch)) throw std::runtime_error("Unexpected EOF in tags");
                bytes_read++;
                if (ch == '\n') throw std::runtime_error("Newline in tag not allowed");
                tag += ch;
                if (ch == '\0') {
                    ciff.tags.push_back(tag);
                    tag.clear();
                }
                if (bytes_read == ciff.header_size && ch != '\0')
                    throw std::runtime_error("Header must end with null terminator");
            }

            // Validate tag endings
            for (const auto& t : ciff.tags) {
                if (t.empty() || t.back() != '\0')
                    throw std::runtime_error("Tag must end with null character");
            }

            // Read pixels
            int64_t pixel_bytes = 0;
            while (pixel_bytes < ciff.content_size) {
                uint8_t rgb[3];
                file.read(reinterpret_cast<char*>(rgb), 3);
                if (file.gcount() != 3) throw std::runtime_error("Incomplete pixel");
                ciff.pixels.emplace_back(rgb[0], rgb[1], rgb[2]);
                pixel_bytes += 3;
            }

            // Check for extra bytes
            if (file.get(ch)) throw std::runtime_error("Extra data after pixels");

        } catch (...) {
            ciff.is_valid = false;
        }

        return ciff;
    }

private:
    static int64_t read_int64(std::ifstream& file) {
        int64_t val;
        file.read(reinterpret_cast<char*>(&val), 8);
        if (file.gcount() != 8) throw std::runtime_error("Failed to read int64");
        return val;
    }
};
//int main() {
//    std::string path = "./test-vectors/test1.ciff";
//    CIFF ciff = CIFF::parse_ciff(path);
//
//    if (ciff.is_valid) {
//        std::cout << "CIFF file parsed successfully!" << std::endl;
//        std::cout << "Magic: " << ciff.magic << std::endl;
//        std::cout << "Width: " << ciff.width << ", Height: " << ciff.height << std::endl;
//        std::cout << "Caption: " << ciff.caption << std::endl;
//        std::cout << "Number of tags: " << ciff.tags.size() << std::endl;
//    } else {
//        std::cerr << "Failed to parse CIFF file." << std::endl;
//    }
//
//    return 0;
//}
extern "C" {
    struct RGBPixel {
        uint8_t r, g, b;
    };

    struct CIFF_Export {
        const char* magic;
        int64_t header_size;
        int64_t content_size;
        int64_t width;
        int64_t height;
        const char* caption;
        const char** tags;
        RGBPixel* pixels;
        bool is_valid;
    };

    __declspec(dllexport) CIFF_Export* parse(const char* path) {
        CIFF ciff = CIFF::parse(path);
        if (!ciff.is_valid) return nullptr;

        CIFF_Export* export_data = new CIFF_Export;
        static char magic_buffer[5];
        strncpy(magic_buffer, ciff.magic.c_str(), 4);
        magic_buffer[4] = '\0';
        export_data->magic = magic_buffer;
        export_data->header_size = ciff.header_size;
        export_data->content_size = ciff.content_size;
        export_data->width = ciff.width;
        export_data->height = ciff.height;

        size_t len = ciff.caption.size();
        char* caption_buffer = new char[len + 1];
        memcpy(caption_buffer, ciff.caption.c_str(), len + 1);
        export_data->caption = caption_buffer;

        // Allocate tags
        export_data->tags = new const char*[ciff.tags.size()];
        for (size_t i = 0; i < ciff.tags.size(); ++i) {
            len = ciff.tags[i].size();
            char* tag_buffer = new char[len + 1];
            memcpy(tag_buffer, ciff.tags[i].c_str(), len + 1);
            export_data->tags[i] = tag_buffer;
        }
        export_data->tags[ciff.tags.size()] = nullptr;

        // Allocate pixels
        size_t pixel_count = ciff.pixels.size();
        export_data->pixels = new RGBPixel[pixel_count];
        for (size_t i = 0; i < pixel_count; ++i) {
            auto& pixel = ciff.pixels[i];
            export_data->pixels[i] = { std::get<0>(pixel), std::get<1>(pixel), std::get<2>(pixel) };
        }

        export_data->is_valid = true;
        return export_data;
    }

    __declspec(dllexport) void free_ciff(CIFF_Export* data) {
        if (!data) return;

        delete[] data->caption;

        if (data->tags) {
            for (size_t i = 0; data->tags[i] != nullptr; ++i) {
                delete[] data->tags[i];
            }
            delete[] data->tags;
        }

        delete[] data->pixels;

        delete data;
    }
}