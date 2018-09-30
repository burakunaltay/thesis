#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <limits.h>
 
void scale(int *in, int scale_factor, size_t arrlen)
{
    unsigned int i = 0;
 
    switch(scale_factor%2)
    {
        case 0:
            for( ; i < arrlen ; i++ )
            {
                in[i] = ( in[i] << (scale_factor/2) );
            }
 
        case 1:
            for( ; i < arrlen ; i++ )
            {
                in[i] = scale_factor*in[i];
            }
        break;
    }
}
 
 
typedef struct arr_element
{
    int index;
    int value;
} arr_element_t;
 
int find_max(int *arr, size_t arrlen)
{
    arr_element_t max;
   
    unsigned int i = 0;
    for( ; i < arrlen ; i++ )
    {
        if( arr[i] > max.value )
        {
            max.value = arr[i];
            max.index = i;
 
        }
    }
 
    return max.value;
}
 
int find_max_index(int *arr, size_t arrlen)
{
    arr_element_t max;
   
    unsigned int i = 0;
    for( ; i < arrlen ; i++ )
    {
        if( arr[i] > max.value )
        {
            max.value = arr[i];
            max.index = i;
 
        }
    }
 
    return max.index;
}
 
int find_min(const int *arr, size_t arrlen)
{
 
    arr_element_t min;
   
    unsigned int i = 0;
    for( ; i < arrlen ; i++ )
    {
        if( arr[i] < min.value )
        {
            min.value = arr[i];
            min.index = i;
        }
    }
 
    return min.value;
}
 
int find_min_index(const int *arr, size_t arrlen)
{
 
    arr_element_t min;
   
    unsigned int i = 0;
    for( ; i < arrlen ; i++ )
    {
        if( arr[i] < min.value )
        {
            min.value = arr[i];
            min.index = i;
        }
    }
 
    return min.index;
}
 
void square_array(int *in, size_t arrlen)
{
    for(int i = 0; i < arrlen ; i++ )
    {
        in[i] *= in[i];
    }
}
 
void divide_array(int *in, int denominator, size_t arrlen)
{
    if(denominator == 0)
    {
        return;
    }
 
    if(denominator%2 == 0)
    {
        for(int i = 0; i < arrlen ; i++ )
        {
            in[i] = ( in[i] >> (denominator/2) );
        }
    }
    else
    {
        for(int i = 0; i < arrlen ; i++ )
        {
            in[i] = in[i] / denominator;
        }      
    }
}
 
void offset_array(int *arr, int offset_value, size_t arrlen)
{
    if (offset_value == 0)
    {
        return;
    }
 
    for( int i = 0; i < arrlen ; i = i+4 )
    {
        arr[i] = arr[i] + offset_value;
        arr[i+1] = arr[i+1] + offset_value;
        arr[i+2] = arr[i+2] + offset_value;
        arr[i+3] = arr[i+3] + offset_value;
    }
}
 
void reverse_array(int *in, int *out, size_t arrlen)
{
    int reversed[ARRLEN];
    for (int i = 0; i < arrlen; ++i)
    {
        reversed[i] = in[ (arrlen-1) - i ];
    }

    out = reversed;
}
 
void clamp_array(int *in, int min, int max, size_t arrlen)
{
    for (int i = 0; i < arrlen; ++i)
    {
        int val = in[i];
        if (val > max)
        {
            in[i] = max;
        }
        else if (val < min)
        {
            in[i] = min;
        }
    }
}
 
void quicksort_internal(int *a, int low, int high);
int split(int *a, int low, int high);
 
void quicksort_internal(int *a, int low, int high)
{
    int middle;
 
    if (low >= high) return;
    middle = split(a, low, high);
    quicksort_internal(a, low, (middle-1));
    quicksort_internal(a, (middle+1), high);
}
 
int split(int *a, int low, int high)
{
    int16_t part_element = a[low];
 
    for (;;) {
        while (low < high && part_element <= a[high]) {
            high--;
        }
        if (low >= high) break;
        a[low++] = a[high];
 
        while (low < high && a[low] <= part_element) {
            low++;
        }
        if (low >= high) break;
        a[high--] = a[low];
    }
 
    a[high] = part_element;
    return high;
}
 
void quicksort(int *in, size_t arrlen)
{
  quicksort_internal(in, 0, arrlen-1);
}
 
int average_array(int *in, size_t arrlen)
{
    int sum = 0;
    for (int i = 0; i < arrlen; ++i)
    {
        sum += in[i];
    }
    return sum / arrlen;
}
 
#define FLAG (0x55)
int custom_filter(int value1, int value2, size_t arrlen)
{
    if((value1 & FLAG) == value2)
    {
        return value1;
    }

    return value2;
}
 
int algorithm(int *arr1, int *arr2, size_t len)
{
    //find both maxes and mins for input arrays
    int min_arr1 = find_min(arr1, len);
    int min_arr2 = find_min(arr2, len);
 
    int max_arr1 = find_max(arr1, len);
    int max_arr2 = find_max(arr2, len);
 
    //find max and min indexes
    int min_index_arr1 = find_min_index(arr1, len);
    int min_index_arr2 = find_min_index(arr2, len);
 
    int max_index_arr1 = find_max_index(arr1, len);
    int max_index_arr2 = find_max_index(arr2, len);
 
    //find averages
    int average1 = average_array(arr1, len);
    int average2 = average_array(arr2, len);
 
    //shave off the average
    offset_array(arr1, len, -average1);
    offset_array(arr2, len, -average2);
 
    //depending on the average
    //square one and scale the
    //other by 2
    if(average1 > average2)
    {
        square_array(arr1, len);
        scale(arr2, len, 2);
    }
    else
    {
        square_array(arr2, len);
        scale(arr1, len, 2);        
    }
 
    //clamp both arrays
    const int clamp_amount = (1<<17);
 
    clamp_array(arr1, -clamp_amount, clamp_amount, len);
    clamp_array(arr2, -clamp_amount, clamp_amount, len);
 
    quicksort(arr1, len-1);
    quicksort(arr2, len-1);
 
    int *reversed_arr2 = (int*)malloc(sizeof(int)*len);
    reverse_array(arr2, reversed_arr2, len);
 
 
    for(int i = 0; i < len; i++)
    {
        arr1[i] = arr1[i] - reversed_arr2[i];
    }
 
 
    int prev_max_index = arr1[max_index_arr1] - max_arr1;
    int prev_min_index = arr1[min_index_arr1] - min_arr1;
 
    divide_array(arr1, len, (prev_min_index + prev_max_index)/2 );
 
    return average_array(arr1, len);
}
 