package org.chater;

import com.google.cloud.vision.v1.AnnotateImageRequest;
import com.google.cloud.vision.v1.AnnotateImageResponse;
import com.google.cloud.vision.v1.BatchAnnotateImagesResponse;
import com.google.cloud.vision.v1.EntityAnnotation;
import com.google.cloud.vision.v1.Feature;
import com.google.cloud.vision.v1.Image;
import com.google.cloud.vision.v1.ImageAnnotatorClient;
import com.google.cloud.vision.v1.ImageAnnotatorSettings;
import com.google.protobuf.ByteString;
import org.apache.kafka.common.metrics.stats.Max;

import java.io.FileInputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Base64;
import java.util.List;

public class DetectText {
    public static String detectText() throws IOException {
        // TODO(developer): Replace these variables before running the sample.
        String filePath = "/other/eater_storage/20241215_001156.jpg";
        return detectText(filePath);
    }
    public static String detectText(String filePath, Boolean debug) throws IOException {
        return "Test run Max 200kg 19.8 kg d=100g ZEEGMA";
    }

    public static String detectText(String filePath) throws IOException {
        List<AnnotateImageRequest> requests = new ArrayList<>();

        byte[] decodedBytes = Base64.getDecoder().decode(filePath);
        ByteString imgBytes = ByteString.copyFrom(decodedBytes);

        Image img = Image.newBuilder().setContent(imgBytes).build();
        Feature feat = Feature.newBuilder().setType(Feature.Type.TEXT_DETECTION).build();
        AnnotateImageRequest request =
                AnnotateImageRequest.newBuilder().addFeatures(feat).setImage(img).build();
        requests.add(request);
        String apiKay = System.getenv("VISION_API_KEY");
        ImageAnnotatorSettings settings = ImageAnnotatorSettings.newBuilder().setApiKey(apiKay).build();
        try (ImageAnnotatorClient client = ImageAnnotatorClient.create(settings)) {
            BatchAnnotateImagesResponse response = client.batchAnnotateImages(requests);
            List<AnnotateImageResponse> responses = response.getResponsesList();

            for (AnnotateImageResponse res : responses) {
                if (res.hasError()) {
                    String error = res.getError().getMessage();
                    System.out.format("Error: %s%n", error);
                    return error;
                }

                // For full list of available annotations, see http://g.co/cloud/vision/docs
                for (EntityAnnotation annotation : res.getTextAnnotationsList()) {
                    String text = annotation.getDescription();
                    System.out.format("Text: %s%n", text);
                    return text;
                }
            }
        }
        return null;
    }

}